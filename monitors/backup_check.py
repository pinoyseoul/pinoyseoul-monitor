# -*- coding: utf-8 -*-
"""
Monitors the age of the latest rclone backup and sends an alert if it's too old.
"""

import subprocess
import datetime
import logging
from typing import Dict, Any, Optional

from utils.google_chat import send_alert
from utils.state_manager import load_state, save_state, is_service_down, mark_service_down, mark_service_up

# Set up a logger for this module
log = logging.getLogger(__name__)

import json

# Define a constant for the service name for state management
BACKUP_SERVICE_NAME = "Server Backup System"

def _get_latest_backup_info(remote: str, state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Gets the latest backup file and its modification time from an rclone remote.
    """
    log.info(f"Checking for latest backup on rclone remote '{remote}'")
    try:
        result = subprocess.run(
            ['rclone', 'lsjson', remote],
            capture_output=True, text=True, check=True
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

    except subprocess.CalledProcessError as e:
        log.error(f"Failed to list files on rclone remote '{remote}': {e.stderr}")
        mark_service_down(BACKUP_SERVICE_NAME, state)
        details = (
            f"<b>What's happening:</b> The monitor can't connect to the backup storage location. This might be due to an issue with the storage provider or the server's network connection.\n"
            f"<b>Impact:</b> We cannot verify if backups are safe.\n\n"
            "<b>What to do:</b> Please contact the technical team at tech@pinoyseoul.com and report that the monitor 'Could Not Access Backup Storage'."
        )
        send_alert("Could Not Access Backup Storage", severity="critical", title="CRITICAL: Backup Monitor Failed", details=details)
        return None
    except Exception as e:
        log.error(f"An unexpected error occurred while checking rclone remote: {e}")
        return None


def check_backup_age(config: Dict[str, Any], portainer_url: str) -> Dict[str, Any]:
    """
    Checks the age of the most recent backup and sends an alert if it's too old.
    """
    remote = config.get('rclone_remote', 'gdrive:PinoySeoul-Backups')
    max_age_hours = config.get('max_age_hours', 25)

    result = {'status': 'error', 'message': 'Check did not run'}
    portainer_button = [{"text": "Manage Server", "url": portainer_url}]
    
    state = load_state()
    backup_info = _get_latest_backup_info(remote, state)

    if not backup_info:
        mark_service_down(BACKUP_SERVICE_NAME, state)
        details = (
            f"<b>What's happening:</b> The monitor checked the backup storage but could not find any recent backup files.\n"
            f"<b>Impact:</b> This is a critical issue. It means the daily server backup process has failed, and your data is not being saved. This puts you at high risk of data loss.\n\n"
            "<b>What to do:</b> Please contact the technical team immediately at tech@pinoyseoul.com and report that 'No Server Backups Were Found'."
        )
        # Avoid sending a duplicate alert if _get_latest_backup_info already sent one
        if "Could Not Access Backup Storage" not in [d.get('title') for d in state.get('down_services', []) if isinstance(d, dict)]:
             send_alert("No Server Backups Found", severity="critical", title="CRITICAL: Backup Check Failed", details=details, extra_buttons=portainer_button)
        result['message'] = "No backups found."
    else:
        backup_age = datetime.datetime.now() - backup_info['mod_time']
        backup_age_hours = backup_age.total_seconds() / 3600

        if backup_age_hours > max_age_hours:
            mark_service_down(BACKUP_SERVICE_NAME, state)
            result['status'] = 'failed'
            result['message'] = f"The latest backup is {backup_age_hours:.1f} hours old, which is older than our {max_age_hours}-hour policy."
            log.critical(result['message'])
            details = (
                f"<b>What's happening:</b> The most recent server backup is {backup_age_hours:.1f} hours old. This is older than the safety limit of {max_age_hours} hours.\n"
                f"<b>Impact:</b> In case of a server failure, we could lose a significant amount of data. This is a high-risk situation.\n\n"
                "<b>What to do:</b> Please contact the technical team immediately at tech@pinoyseoul.com and report that the 'Server Backup is Too Old'."
            )
            send_alert("Server Backup is Too Old", severity="critical", title="CRITICAL: Backup Check Failed", details=details, extra_buttons=portainer_button)
        else:
            result['status'] = 'success'
            result['message'] = f"Latest backup is {backup_age_hours:.1f} hours old (within {max_age_hours}-hour limit)."
            log.info(result['message'])
            if is_service_down(BACKUP_SERVICE_NAME, state):
                details = "<b>What happened:</b> The issue affecting the server backup system has been resolved. New backups are now being created and saved successfully."
                send_alert("The backup system is now working correctly", severity="info", title="ALL CLEAR: Backup System Restored", details=details)
                mark_service_up(BACKUP_SERVICE_NAME, state)

    save_state(state)
    return result