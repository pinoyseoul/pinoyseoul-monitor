# -*- coding: utf-8 -*-
"""
Monitors the age of the latest rclone backup and sends an alert if it's too old.
Implements a "two-strikes" policy to avoid alerts for transient failures.
"""

import subprocess
import datetime
import logging
from typing import Dict, Any, Optional

from utils.google_chat import send_alert
from utils.state_manager import (
    load_state, save_state, is_service_down, 
    mark_service_down, mark_service_up,
    increment_failure_count, get_failure_count, reset_failure_count
)

# Set up a logger for this module
log = logging.getLogger(__name__)

import json

# Define a constant for the service name for state management
BACKUP_SERVICE_NAME = "Server Backup System"

def _get_latest_backup_info(remote: str) -> Optional[Dict[str, Any]]:
    """
    Gets the latest backup file and its modification time from an rclone remote.
    """
    log.info(f"Checking for latest backup on rclone remote '{remote}'")
    try:
        result = subprocess.run(
            ['rclone', 'lsjson', remote],
            capture_output=True, text=True, check=True, timeout=300 # 5-minute timeout
        )
        files = json.loads(result.stdout)
        
        if not files:
            log.warning(f"No files found on rclone remote '{remote}'")
            return None

        latest_backup = None
        latest_time = None

        for file_info in files:
            path = file_info.get("Path")
            if not path or not path.endswith('.tar.gz'):
                continue
            
            try:
                time_str = file_info.get("ModTime")
                mod_time = datetime.datetime.fromisoformat(time_str.replace('Z', '+00:00'))
                mod_time = mod_time.replace(tzinfo=None)

                if latest_time is None or mod_time > latest_time:
                    latest_time = mod_time
                    latest_backup = path
            except (ValueError, KeyError) as e:
                log.error(f"Could not parse file info from rclone output: '{file_info}'. Error: {e}")
                continue
        
        if latest_backup is None:
            log.warning(f"No .tar.gz files found on rclone remote '{remote}'")
            return None

        log.info(f"Latest backup found: '{latest_backup}' with modification time {latest_time}")
        return {'path': latest_backup, 'mod_time': latest_time}

    except subprocess.TimeoutExpired:
        log.error(f"Timeout expired while listing files on rclone remote '{remote}'. The storage provider may be slow or unresponsive.")
        return None # Treat timeout as a failure to find info
    except subprocess.CalledProcessError as e:
        log.error(f"Failed to list files on rclone remote '{remote}': {e.stderr}")
        # This alert is sent immediately because it indicates a fundamental connectivity issue.
        details = (
            f"<b>What's happening:</b> Our system can't reach the place where your important files are usually saved. This might be a problem with the online storage service or our server's internet connection.\n"
            f"<b>Impact:</b> We don't know if your latest backups are safe. This means your data might be at risk if something goes wrong.\n\n"
            "<b>What to do:</b> Please tell the technical team right away at tech@pinoyseoul.com that 'The backup system can't connect to storage'."
        )
        send_alert("Can't check if your files are backed up", severity="critical", title="CRITICAL: Backup System Offline", details=details)
        return None
    except Exception as e:
        log.error(f"An unexpected error occurred while checking rclone remote: {e}")
        return None


def check_backup_age(config: Dict[str, Any], portainer_url: str) -> Dict[str, Any]:
    """
    Checks the age of the most recent backup and sends an alert if it's too old,
    following a "two-strikes" policy.
    """
    remote = config.get('rclone_remote', 'gdrive:PinoySeoul-Backups')
    max_age_hours = config.get('max_age_hours', 25)
    failure_threshold = config.get('failure_threshold', 2)

    result = {'status': 'error', 'message': 'Check did not run'}
    portainer_button = [{"text": "Manage Server", "url": portainer_url}]
    
    state = load_state()
    backup_info = _get_latest_backup_info(remote)

    # --- Failure Condition ---
    if not backup_info or (datetime.datetime.now() - backup_info['mod_time']).total_seconds() / 3600 > max_age_hours:
        increment_failure_count(BACKUP_SERVICE_NAME, state)
        failure_count = get_failure_count(BACKUP_SERVICE_NAME, state)
        
        result['status'] = 'failed'
        
        if not backup_info:
            result['message'] = "No recent backup file found."
        else:
            backup_age_hours = (datetime.datetime.now() - backup_info['mod_time']).total_seconds() / 3600
            result['message'] = f"The latest backup is {backup_age_hours:.1f} hours old, which is older than our {max_age_hours}-hour policy."
        
        log.warning(f"{result['message']} (Failure {failure_count} of {failure_threshold})")

        # --- Alerting on Second Strike ---
        if failure_count >= failure_threshold:
            log.critical(f"Backup failure threshold reached. Sending critical alert.")
            details = (
                f"<b>What's happening:</b> The monitor has detected that the server backup has failed multiple times in a row.\n"
                f"<b>Impact:</b> This is a critical issue. Your data is not being saved, putting you at high risk of data loss.\n\n"
                "<b>What to do:</b> Please contact the technical team immediately at tech@pinoyseoul.com and report that the 'Server Backup is Failing Repeatedly'."
            )
            send_alert("Server Backup Failing Repeatedly", severity="critical", title="CRITICAL: Backup System Failure", details=details, extra_buttons=portainer_button)
            # Reset count after alerting to prevent spam
            reset_failure_count(BACKUP_SERVICE_NAME, state)
    
    # --- Success Condition ---
    else:
        backup_age_hours = (datetime.datetime.now() - backup_info['mod_time']).total_seconds() / 3600
        result['status'] = 'success'
        result['message'] = f"Latest backup is {backup_age_hours:.1f} hours old (within {max_age_hours}-hour limit)."
        log.info(result['message'])

        # --- "All Clear" Logic ---
        if is_service_down(BACKUP_SERVICE_NAME, state):
            log.info("Backup service was previously failing and is now healthy. Sending 'All Clear' alert.")
            details = "<b>What happened:</b> The issue affecting the server backup system has been resolved. New backups are now being created and saved successfully."
            send_alert("The backup system is now working correctly", severity="info", title="ALL CLEAR: Backup System Restored", details=details)
            mark_service_up(BACKUP_SERVICE_NAME, state) # This also resets the failure count implicitly

    save_state(state)
    return result