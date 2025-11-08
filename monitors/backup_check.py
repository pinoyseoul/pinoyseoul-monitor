# -*- coding: utf-8 -*-
"""
Monitors the age of the latest rclone backup and sends an alert if it's too old.
"""

import subprocess
import datetime
import logging
from typing import Dict, Any, Optional

from utils.google_chat import send_alert

# Set up a logger for this module
log = logging.getLogger(__name__)

import json

def _get_latest_backup_info(remote: str) -> Optional[Dict[str, Any]]:
    """
    Gets the latest backup file and its modification time from an rclone remote
    by parsing JSON output for maximum compatibility.
    """
    log.info(f"Checking for latest backup on rclone remote '{remote}'")
    try:
        # Use 'lsjson' which is the correct command for older rclone versions
        result = subprocess.run(
            ['rclone', 'lsjson', remote],
            capture_output=True,
            text=True,
            check=True
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
                # rclone's time format is RFC3339 (e.g., "2023-11-04T10:00:00Z")
                time_str = file_info.get("ModTime")
                # Python's fromisoformat can handle the 'Z' suffix in 3.7+
                mod_time = datetime.datetime.fromisoformat(time_str.replace('Z', '+00:00'))
                # Make it timezone-naive for comparison with datetime.now()
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
        return None
    except json.JSONDecodeError as e:
        log.error(f"Failed to decode JSON from rclone output: {e}")
        return None
    except Exception as e:
        log.error(f"An unexpected error occurred while checking rclone remote: {e}")
        return None


def check_backup_age(config: Dict[str, Any], portainer_url: str) -> Dict[str, Any]:
    """
    Checks the age of the most recent backup and sends an alert if it's too old.
    """
    remote = config.get('rclone_remote', 'gdrive:PinoySeoul-Backups')
    max_age_hours = config.get('max_age_hours', 72) # Default to 3 days

    result = {
        'status': 'error',
        'last_backup_time': None,
        'last_backup_file': None,
        'message': 'Check did not run'
    }

    backup_info = _get_latest_backup_info(remote)

    if not backup_info:
        msg = f"What happened: The monitor checked the backup storage but could not find any recent backup files. This could mean the backup process is failing."
        log.critical(msg)
        send_alert("No Server Backups Found", severity="critical", title="Backup Check Failed", details=msg, portainer_url=portainer_url)
        result['message'] = "No backups found."
        return result

    result.update({
        'last_backup_time': backup_info['mod_time'],
        'last_backup_file': backup_info['path'],
    })

    backup_age = datetime.datetime.now() - backup_info['mod_time']
    backup_age_hours = backup_age.total_seconds() / 3600

    if backup_age_hours > max_age_hours:
        result['status'] = 'failed'
        result['message'] = f"The latest backup is {backup_age_hours:.1f} hours old, which is older than our {max_age_hours}-hour policy."
        log.critical(result['message'])
        send_alert("Server Backup is Too Old", severity="critical", title="Backup Check Failed",
                   details=f"Impact: The most recent server backup is from {backup_age_hours:.1f} hours ago. If the server fails, we could lose a significant amount of data. This needs to be investigated.", portainer_url=portainer_url)
    else:
        result['status'] = 'success'
        result['message'] = f"Latest backup is {backup_age_hours:.1f} hours old (within {max_age_hours}-hour limit)."
        log.info(result['message'])

    return result