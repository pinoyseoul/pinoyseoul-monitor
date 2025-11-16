# -*- coding: utf-8 -*-
"""
Monitors AzuraCast to provide a daily summary of listener statistics.
"""

import logging
import requests
from datetime import datetime
from typing import Dict, Any

from utils.google_chat import send_azuracast_summary, send_alert
from utils.quotes import get_random_quote

log = logging.getLogger(__name__)

def get_listener_summary(monitor_config: Dict[str, Any], integrations_config: Dict[str, Any], state: Dict[str, Any]):
    """
    Connects to the AzuraCast API, fetches the listener report for the day,
    and sends a formatted summary to Google Chat.
    """
    options = monitor_config.get('options', {})
    api_base_url = options.get('api_base_url')
    api_key = options.get('api_key')
    station_id = options.get('station_id')
    station_name = options.get('station_name', str(station_id))

    if not all([api_base_url, api_key, station_id]):
        log.error("AzuraCast config is missing required fields (api_base_url, api_key, station_id).")
        return

    today_str = datetime.now().strftime('%Y-%m-%d')
    api_url = f"{api_base_url}/station/{station_id}/reports/overview/charts?start={today_str}&end={today_str}"
    headers = {'Authorization': f'Bearer {api_key}'}

    try:
        log.info(f"Fetching daily listener report from AzuraCast for station '{station_id}'...")
        response = requests.get(api_url, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()

        unique_listeners = None
        # Find the 'unique listeners' metric instead of assuming its position
        for metric in data.get('daily', {}).get('metrics', []):
            metric_name = metric.get('name', '').lower()
            if 'listeners' in metric_name:
                if metric.get('data') and len(metric['data']) > 0:
                    unique_listeners = metric['data'][0].get('y', 0)
                    break
        
        if unique_listeners is None:
            log.error("Could not find 'unique listeners' metric in AzuraCast API response.")
            send_alert(
                message="The monitor received an unexpected response from the radio server.",
                severity="warning",
                title="Could Not Parse Listener Report",
                details="The listener summary could not be generated because the API response from AzuraCast was in an unexpected format."
            )
            return

        log.info(f"Successfully fetched daily unique listener count: {unique_listeners}")
        evening_quote = get_random_quote('evening')
        send_azuracast_summary(
            listeners_total=unique_listeners,
            station_name=station_name,
            quote=evening_quote
        )

    except requests.exceptions.RequestException as e:
        log.error(f"Failed to connect to AzuraCast API: {e}")
        send_alert(
            message="The monitor could not connect to the radio server to get the daily listener report.",
            severity="warning",
            title="Could Not Fetch Listener Report",
            details=f"This usually happens if the radio service is temporarily down or restarting. The error was: {str(e)}"
        )
    except Exception as e:
        log.error(f"An unexpected error occurred while fetching AzuraCast data: {e}", exc_info=True)
        send_alert(
            message="An unexpected error occurred while generating the listener report.",
            severity="warning",
            title="Listener Report Failed",
            details=f"The report could not be generated due to an internal error: {str(e)}"
        )
