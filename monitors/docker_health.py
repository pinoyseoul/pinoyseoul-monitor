# -*- coding: utf-8 -*-
"""
Monitors the health of all Docker containers on the local daemon, sending
alerts for specific conditions like stopped containers or restart loops.
Includes auto-remediation for stopped containers and stateful 'resolved' alerts.
"""

import docker
from datetime import datetime, timezone, timedelta
import logging
from typing import Dict, Any

# Assuming this module is run in an environment where utils can be imported
from utils.google_chat import send_alert
from utils.state_manager import load_state, save_state, is_service_down, mark_service_down, mark_service_up

# Set up a logger for this module
log = logging.getLogger(__name__)

# --- Main Function ---

def check_docker_health(name_map: Dict[str, str], portainer_url: str, state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Connects to Docker, checks all containers, attempts to auto-fix stopped
    containers, sends alerts for issues, and sends 'resolved' messages.
    """
    summary = {
        'total_containers': 0,
        'running': 0,
        'stopped': 0,
        'issues': [],
        'status': 'healthy'
    }
    portainer_button = [{"text": "Manage Server", "url": portainer_url}]
    
    try:
        client = docker.from_env(timeout=10)
        client.ping()
        containers = client.containers.list(all=True)
    except docker.errors.DockerException as e:
        log.error(f"Could not connect to Docker daemon: {e}")
        details = (
            "<b>What's happening:</b> The monitor can't connect to the main Docker service on the server. This is a major problem and likely means all services are offline.\n\n"
            "<b>What to do:</b> Please contact the technical team immediately at tech@pinoyseoul.com and report that the 'Docker Service is Unavailable'."
        )
        send_alert("All Services May Be Down", severity="critical", title="CRITICAL: Cannot Connect to Docker", details=details)
        summary['status'] = 'critical'
        return summary
    
    if not containers:
        log.warning("No Docker containers found on this system.")
        return summary # No need to alert if there are no containers to monitor

    summary['total_containers'] = len(containers)
    
    for container in containers:
        status = container.status
        name = container.name
        friendly_name = name_map.get(name, name)

        if status == 'running':
            summary['running'] += 1
            
            # --- STATEFUL 'RESOLVED' LOGIC ---
            if is_service_down(name, state):
                log.info(f"Service '{name}' was down and is now running. Sending 'resolved' alert.")
                details = f"<b>What happened:</b> The issue affecting the <b>{friendly_name}</b> service has been resolved. It is now back online and operating normally."
                send_alert(
                    message=f"The {friendly_name} service is back online.",
                    severity="info",
                    title=f"ALL CLEAR: {friendly_name} Service Restored",
                    details=details
                )
                mark_service_up(name, state)

        elif status in ['exited', 'dead']:
            summary['stopped'] += 1
            log.warning(f"Container '{name}' is stopped. Attempting to restart...")
            mark_service_down(name, state)
            
            # --- AUTO-FIX LOGIC ---
            try:
                container.start()
                log.info(f"Successfully restarted container '{name}'.")
                details = (
                    f"<b>What happened:</b> The monitor found the <b>{friendly_name}</b> service was offline and automatically restarted it.\n\n"
                    "<b>What to do:</b> No action is needed from you right now. The service should be back online. If you get this message frequently, please let the technical team know."
                )
                send_alert(
                    message=f"The {friendly_name} service was found offline and has been automatically restarted.",
                    severity="info",
                    title=f"Auto-Recovery: {friendly_name} Restarted",
                    details=details,
                    extra_buttons=portainer_button
                )
                # Mark as up since we fixed it, so we don't get a "resolved" message on the next run
                mark_service_up(name, state)
                if summary['status'] != 'critical':
                    summary['status'] = 'warning'
            except docker.errors.APIError as e:
                log.critical(f"Failed to restart container '{name}': {e}")
                details = (
                    f"<b>What's happening:</b> The <b>{friendly_name}</b> service is offline. The monitor tried to restart it automatically but failed.\n"
                    f"<b>Impact:</b> This service is completely unavailable.\n\n"
                    "<b>What to do:</b> Please contact the technical team at tech@pinoyseoul.com and report that the '{friendly_name}' service is down and could not be auto-restarted."
                )
                send_alert(
                    message=f"The {friendly_name} service is offline and could not be restarted.",
                    severity="critical",
                    title=f"CRITICAL: {friendly_name} Service Down",
                    details=details,
                    extra_buttons=portainer_button
                )
                summary['issues'].append(name)
                summary['status'] = 'critical'

        elif status == 'restarting':
            summary['stopped'] += 1
            log.critical(f"Container '{name}' is in a restart loop.")
            mark_service_down(name, state)
            details = (
                f"<b>What's happening:</b> The <b>{friendly_name}</b> service is unstable and crashing repeatedly. This is a serious issue that the auto-restart feature cannot fix.\n"
                f"<b>Impact:</b> The service is completely unavailable.\n\n"
                "<b>What to do:</b> Please contact the technical team immediately at tech@pinoyseoul.com and report that the '{friendly_name}' service is in a 'Crash Loop'."
            )
            send_alert(
                message=f"The {friendly_name} service is unstable and repeatedly crashing.",
                severity="critical",
                title=f"CRITICAL: {friendly_name} Service Unstable",
                details=details,
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
    
    # Mock state for testing purposes
    mock_state = {'down_services': [], 'failure_counts': {}}
    
    result = check_docker_health(name_map=mock_name_map, portainer_url="", state=mock_state)
    
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