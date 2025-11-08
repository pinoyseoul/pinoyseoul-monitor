# -*- coding: utf-8 -*-
"""
Monitors AzuraCast to provide a daily summary of listener statistics.
"""

import logging
import requests
from datetime import datetime
from typing import Dict, Any

from utils.google_chat import send_azuracast_summary, send_alert

log = logging.getLogger(__name__)

def get_listener_summary(config: Dict[str, Any], evening_quote: str = None) -> bool:
    """
    Connects to the AzuraCast API, fetches the listener report for the day,
    and sends a formatted summary to Google Chat.
    """
    api_base_url = config.get('api_base_url')
    api_key = config.get('api_key')
    station_id = config.get('station_id')
    station_name = config.get('station_name', str(station_id))

    if not all([api_base_url, api_key, station_id]):
        log.error("AzuraCast config is missing required fields (api_base_url, api_key, station_id).")
        return False

    today_str = datetime.now().strftime('%Y-%m-%d')
    api_url = f"{api_base_url}/station/{station_id}/reports/overview/charts?start={today_str}&end={today_str}"
    headers = {'Authorization': f'Bearer {api_key}'}

    try:
        log.info(f"Fetching daily listener report from AzuraCast for station '{station_id}'...")
        response = requests.get(api_url, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()

        try:
            unique_listeners = data['daily']['metrics'][0]['data'][0]['y']
        except (KeyError, IndexError):
            log.error("Could not parse unique listener count from AzuraCast API response.")
            unique_listeners = 0

        log.info(f"Successfully fetched daily unique listener count: {unique_listeners}")
        send_azuracast_summary(
            listeners_total=unique_listeners,
            station_name=station_name,
            quote=evening_quote
        )
        return True

    except requests.exceptions.RequestException as e:
        log.error(f"Failed to connect to AzuraCast API: {e}")
        send_alert(
            message="The monitor could not connect to the radio server to get the daily listener report.",
            severity="warning",
            title="Could Not Fetch Listener Report",
            details=f"This usually happens if the radio service is temporarily down or restarting. The error was: {str(e)}"
        )
        return False
    except Exception as e:
        log.error(f"An unexpected error occurred while fetching AzuraCast data: {e}")
        return False
