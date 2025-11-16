# -*- coding: utf-8 -*-
"""
Monitors the health of all Docker containers on the local daemon, sending
alerts for specific conditions like stopped containers or restart loops.
Includes auto-remediation for stopped containers and stateful 'resolved' alerts.
"""

import docker
import logging
from typing import Dict, Any

from utils.google_chat import send_alert
from utils.state_manager import is_service_down, mark_service_down, mark_service_up

log = logging.getLogger(__name__)

def check_docker_health(monitor_config: Dict[str, Any], integrations_config: Dict[str, Any], state: Dict[str, Any], send_alerts: bool = True) -> Dict[str, Any]:
    """
    Connects to Docker, checks all containers, attempts to auto-fix stopped
    containers, and sends alerts for issues.
    """
    summary = {
        'total_containers': 0,
        'running': 0,
        'stopped': 0,
        'issues': [],
        'status': 'healthy'
    }
    
    options = monitor_config.get('options', {})
    name_map = options.get('container_name_mapping', {})
    alert_on_recovery = monitor_config.get('alert_on_recovery', False)
    
    portainer_url = integrations_config.get('portainer_url')
    portainer_button = [{"text": "Manage Server", "url": portainer_url}] if portainer_url else []

    try:
        client = docker.from_env(timeout=10)
        client.ping()
        containers = client.containers.list(all=True)
    except docker.errors.DockerException as e:
        log.error(f"Could not connect to Docker daemon: {e}")
        if send_alerts:
            details = (
                "<b>What's happening:</b> The monitor can't connect to the main Docker service on the server. This is a major problem and likely means all services are offline.\n\n"
                "<b>What to do:</b> Please contact the technical team immediately at tech@pinoyseoul.com and report that the 'Docker Service is Unavailable'."
            )
            send_alert("All Services May Be Down", severity="critical", title="CRITICAL: Cannot Connect to Docker", details=details)
        summary['status'] = 'critical'
        return summary

    if not containers:
        log.warning("No Docker containers found on this system.")
        return summary

    summary['total_containers'] = len(containers)

    for container in containers:
        status = container.status
        name = container.name
        friendly_name = name_map.get(name, name)

        if status == 'running':
            summary['running'] += 1
            if is_service_down(name, state):
                log.info(f"Service '{name}' was down and is now running.")
                if send_alerts and alert_on_recovery:
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
            
            try:
                container.start()
                log.info(f"Successfully restarted container '{name}'.")
                if send_alerts and alert_on_recovery:
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
                mark_service_up(name, state)
                if summary['status'] != 'critical':
                    summary['status'] = 'warning'
            except docker.errors.APIError as e:
                log.critical(f"Failed to restart container '{name}': {e}")
                if send_alerts:
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
            if send_alerts:
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