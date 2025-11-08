# -*- coding: utf-8 -*-
"""
Monitors the health of all Docker containers on the local daemon, sending
alerts for specific conditions like stopped containers or restart loops.
"""

import docker
from datetime import datetime, timezone, timedelta
import logging
from typing import Dict, Any, List, Tuple

# Assuming this module is run in an environment where utils can be imported
from utils.google_chat import send_alert

# Set up a logger for this module
log = logging.getLogger(__name__)

    # --- Main Function ---

def check_docker_health(name_map: Dict[str, str], portainer_url: str) -> Dict[str, Any]:
    """
    Connects to Docker, checks all containers, sends alerts for issues,
    and returns a summary of the system's state.

    Args:
        name_map (Dict[str, str]): A dictionary mapping technical container
                                   names to user-friendly names.

    Alert Logic:
    - CRITICAL: Container is stopped, exited, or in a restart loop.
    - WARNING: Container has restarted recently but is now running.
    - INFO: No individual alerts are sent for healthy containers.

    Error Handling:
    - Sends a CRITICAL alert if the Docker daemon is unreachable or if there's
      a permission error.

    Returns:
        A dictionary summarizing the state of all containers.
    """
    summary = {
        'total_containers': 0,
        'running': 0,
        'stopped': 0,
        'issues': [],
        'status': 'healthy' # Can become 'warning' or 'critical'
    }
    portainer_button = [{"text": "View in Portainer", "url": portainer_url}]
    try:
        client = docker.from_env(timeout=10)
        client.ping()
        containers = client.containers.list(all=True)
    except docker.errors.DockerException as e:
        log.error(f"Could not connect to Docker daemon: {e}")
        if 'permission denied' in str(e).lower():
            details = "Fix: Add the current user to the 'docker' group with 'sudo usermod -aG docker $USER' and then log out and back in."
            send_alert("Docker Permission Denied", severity="critical", title="Docker Monitor Failed", details=details, extra_buttons=portainer_button)
        else:
            send_alert("Docker Daemon Unreachable", severity="critical", title="Docker Monitor Failed", details="The monitoring script could not connect to the Docker service.", extra_buttons=portainer_button)
        summary['status'] = 'critical'
        return summary
    
    if not containers:
        log.warning("No Docker containers found on this system.")
        send_alert("No Containers Found", severity="warning", title="Docker Monitor Anomaly", details="The script ran successfully but did not find any containers to monitor.", extra_buttons=portainer_button)
        summary['status'] = 'warning'
        return summary

    summary['total_containers'] = len(containers)
    
    for container in containers:
        status = container.status
        name = container.name
        friendly_name = name_map.get(name, name)

        if status == 'running':
            summary['running'] += 1
            # Check for recent restarts, which could indicate a problem
            try:
                state_attrs = container.attrs.get('State', {})
                restart_count = container.attrs.get('RestartCount', 0)
                started_at_str = state_attrs.get('StartedAt')
                
                if restart_count > 0 and started_at_str:
                    # Parse the timestamp (e.g., "2025-11-08T08:53:27.123456789Z")
                    started_at = datetime.fromisoformat(started_at_str.replace('Z', '+00:00'))
                    # If it started within the last 5 minutes, it's a recent restart
                    if datetime.now(timezone.utc) - started_at < timedelta(minutes=5):
                        log.warning(f"Container '{name}' has restarted recently.")
                        send_alert(
                            message=f"The {friendly_name} service just restarted but is now running.",
                            severity="warning",
                            title=f"{friendly_name} Restarted",
                            details="Now running normally. Monitoring for further issues. No action needed at this time.",
                            extra_buttons=portainer_button
                        )
                        summary['issues'].append(name)
                        if summary['status'] != 'critical':
                            summary['status'] = 'warning'
            except Exception as e:
                log.error(f"Could not parse restart status for container {name}: {e}")

        elif status in ['exited', 'dead']:
            summary['stopped'] += 1
            log.critical(f"Container '{name}' is stopped with status: {status}")
            send_alert(
                message=f"The {friendly_name} service is offline.",
                severity="critical",
                title=f"{friendly_name} Service Down",
                details=f"Impact: This service is unavailable. Nash has been notified.",
                extra_buttons=portainer_button
            )
            summary['issues'].append(name)
            summary['status'] = 'critical'

        elif status == 'restarting':
            summary['stopped'] += 1 # It's not in a healthy 'running' state
            log.critical(f"Container '{name}' is in a restart loop.")
            send_alert(
                message=f"The {friendly_name} service is caught in a restart loop.",
                severity="critical",
                title=f"{friendly_name} Service Unstable",
                details=f"Impact: The service is repeatedly crashing. This requires immediate investigation. Nash has been notified.",
                extra_buttons=portainer_button
            )
            summary['issues'].append(name)
            summary['status'] = 'critical'

    log.info(f"Docker health check complete. Final status: {summary['status']}")
    return summary

if __name__ == '__main__':
    # This block allows for direct testing of the module.
    # It requires Docker to be running and will send REAL alerts.
    print("--- Running Docker Health Check Module ---")
    print("This will connect to your local Docker daemon and may send alerts.")
    
    # In a real test, this map would come from a loaded config file.
    mock_name_map = {
        "kimai": "Kimai Time Tracking",
        "portainer": "Portainer UI"
    }
    
    result = check_docker_health(name_map=mock_name_map)
    
    print("\n--- Check Complete ---")
    print(f"  Overall Status: {result['status']}")
    print(f"  Total Containers: {result['total_containers']}")
    print(f"  Running: {result['running']}")
    print(f"  Stopped/Issues: {result['stopped']}")
    print(f"  Containers with issues: {result['issues']}")
    print("----------------------")
    
    if result['status'] == 'healthy':
        print("\nAll containers appear to be healthy.")
    else:
        print("\nIssues were detected. Please check your Google Chat room for alerts.")