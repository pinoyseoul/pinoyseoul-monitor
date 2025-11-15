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

        unique_listeners = 0
        try:
            # Find the 'unique listeners' metric instead of assuming it's the first one.
            for metric in data.get('daily', {}).get('metrics', []):
                # The metric name can be 'unique_listeners' or 'Unique Listeners', etc.
                metric_name = metric.get('name', '').lower()
                if 'listeners' in metric_name:
                    # The data is for a single day, so we expect one value.
                    if metric.get('data') and len(metric['data']) > 0:
                        unique_listeners = metric['data'][0].get('y', 0)
                        break # Exit loop once found
            else: # This 'else' belongs to the 'for' loop
                log.error("Could not find the 'unique listeners' metric in the AzuraCast API response.")

        except (KeyError, IndexError, TypeError) as e:
            log.error(f"Could not parse unique listener count from AzuraCast API response: {e}")
            # unique_listeners is already 0


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
