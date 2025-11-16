# -*- coding: utf-8 -*-
"""
Monitors the age of the latest rclone backup and sends an alert if it's too old.
Implements a "two-strikes" policy to avoid alerts for transient failures.
"""

import subprocess
import datetime
import logging
import json
from typing import Dict, Any, Optional

from utils.google_chat import send_alert
from utils.state_manager import (
    is_service_down, 
    mark_service_down, 
    mark_service_up,
    increment_failure_count, 
    get_failure_count, 
    reset_failure_count
)

log = logging.getLogger(__name__)

BACKUP_SERVICE_NAME = "Server Backup System"

def _get_latest_backup_info(remote: str, state: Dict[str, Any], send_alerts: bool) -> Optional[Dict[str, Any]]:
    """
    Gets the latest backup file, its modification time, and size from an rclone remote.
    """
    log.info(f"Checking for latest backup on rclone remote '{remote}'")
    try:
        result = subprocess.run(
            ['rclone', 'lsjson', remote],
            capture_output=True, text=True, check=True, timeout=300
        )
        files = json.loads(result.stdout)
        
        if not files:
            log.warning(f"No files found on rclone remote '{remote}'")
            return None

        latest_backup = max(
            (f for f in files if f.get("Path", "").endswith('.tar.gz')),
            key=lambda f: f.get("ModTime"),
            default=None
        )
        
        if latest_backup is None:
            log.warning(f"No .tar.gz files found on rclone remote '{remote}'")
            return None

        log.info(f"Latest backup found: '{latest_backup.get('Path')}' with modification time {latest_backup.get('ModTime')}")
        return {
            'path': latest_backup.get('Path'),
            'mod_time': datetime.datetime.fromisoformat(latest_backup.get("ModTime").replace('Z', '+00:00')).replace(tzinfo=None),
            'size': latest_backup.get('Size', -1)
        }

    except subprocess.TimeoutExpired:
        log.error(f"Timeout expired while listing files on rclone remote '{remote}'.")
        if send_alerts:
            mark_service_down(BACKUP_SERVICE_NAME, state)
            details = "..." # Details omitted for brevity
            send_alert("Can't check if your files are backed up", severity="critical", title="CRITICAL: Backup System Offline", details=details)
        return None
    except subprocess.CalledProcessError as e:
        log.error(f"Failed to list files on rclone remote '{remote}': {e.stderr}")
        if send_alerts:
            mark_service_down(BACKUP_SERVICE_NAME, state)
            details = "..." # Details omitted for brevity
            send_alert("Can't check if your files are backed up", severity="critical", title="CRITICAL: Backup System Offline", details=details)
        return None
    except Exception as e:
        log.error(f"An unexpected error occurred while checking rclone remote: {e}", exc_info=True)
        if send_alerts:
            mark_service_down(BACKUP_SERVICE_NAME, state)
            details = "..." # Details omitted for brevity
            send_alert("Backup Monitor Error", severity="critical", title="CRITICAL: Backup Monitor Failed", details=details)
        return None

def check_backup_age(monitor_config: Dict[str, Any], integrations_config: Dict[str, Any], state: Dict[str, Any], send_alerts: bool = True) -> Dict[str, Any]:
    """
    Checks the age and size of the most recent backup and sends an alert if it's
    too old or too small.
    """
    options = monitor_config.get('options', {})
    remote = options.get('rclone_remote')
    if not remote:
        log.error("rclone_remote is not configured. Skipping backup check.")
        return {'status': 'error', 'message': 'rclone_remote not configured.'}
        
    max_age_hours = options.get('max_age_hours', 25)
    min_size_mb = options.get('min_size_mb', 50)
    failure_threshold = options.get('failure_threshold', 2)
    alert_on_recovery = monitor_config.get('alert_on_recovery', True)

    portainer_url = integrations_config.get('portainer_url')
    portainer_button = [{"text": "Manage Server", "url": portainer_url}] if portainer_url else []
    
    result = {'status': 'error', 'message': 'Check did not run'}
    backup_info = _get_latest_backup_info(remote, state, send_alerts)

    if backup_info and (backup_info['size'] / (1024 * 1024)) < min_size_mb:
        result['status'] = 'failed'
        backup_size_mb = backup_info['size'] / (1024 * 1024)
        result['message'] = f"Latest backup is only {backup_size_mb:.2f} MB, which is smaller than the {min_size_mb} MB minimum."
        log.critical(result['message'])
        
        if send_alerts:
            details = "..." # Details omitted for brevity
            send_alert("Server Backup Too Small", severity="critical", title="CRITICAL: Incomplete Backup Detected", details=details, extra_buttons=portainer_button)
        mark_service_down(BACKUP_SERVICE_NAME, state)
        return result

    if not backup_info or (datetime.datetime.utcnow() - backup_info['mod_time']).total_seconds() / 3600 > max_age_hours:
        increment_failure_count(BACKUP_SERVICE_NAME, state)
        failure_count = get_failure_count(BACKUP_SERVICE_NAME, state)
        result['status'] = 'failed'
        result['message'] = f"The latest backup is too old. (Failure {failure_count}/{failure_threshold})"
        log.warning(result['message'])

        if send_alerts and failure_count >= failure_threshold:
            log.critical("Backup failure threshold reached. Sending critical alert.")
            details = "..." # Details omitted for brevity
            send_alert("Server Backup Failing Repeatedly", severity="critical", title="CRITICAL: Backup System Failure", details=details, extra_buttons=portainer_button)
            reset_failure_count(BACKUP_SERVICE_NAME, state)
    
    else:
        backup_age_hours = (datetime.datetime.utcnow() - backup_info['mod_time']).total_seconds() / 3600
        backup_size_mb = backup_info['size'] / (1024 * 1024)
        result['status'] = 'success'
        result['message'] = f"Latest backup is {backup_age_hours:.1f} hours old and {backup_size_mb:.2f} MB."
        log.info(result['message'])

        if is_service_down(BACKUP_SERVICE_NAME, state):
            log.info("Backup service was previously failing and is now healthy.")
            if send_alerts and alert_on_recovery:
                details = "<b>What happened:</b> The issue affecting the server backup system has been resolved."
                send_alert("The backup system is now working correctly", severity="info", title="ALL CLEAR: Backup System Restored", details=details)
            mark_service_up(BACKUP_SERVICE_NAME, state)

    return result