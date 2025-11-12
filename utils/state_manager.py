# -*- coding: utf-8 -*-
"""
Manages the state of the monitoring system, allowing it to remember
the status of services between checks, including failure counts.
"""

import json
import logging
import os
from typing import Dict, Any

log = logging.getLogger(__name__)

STATE_FILE_PATH = os.path.join(os.path.dirname(__file__), '..', 'monitor_state.json')

def load_state() -> Dict[str, Any]:
    """
    Loads the monitor's state from a JSON file.

    Returns:
        A dictionary representing the last known state. Returns a default
        structure if the file doesn't exist or is invalid.
        It also handles migrating the old list-based state to the new dict-based state.
    """
    default_state = {'down_services': {}}
    if not os.path.exists(STATE_FILE_PATH):
        return default_state
    
    try:
        with open(STATE_FILE_PATH, 'r') as f:
            state = json.load(f)
            
            # Backwards compatibility: migrate from old list format to new dict format
            if isinstance(state.get('down_services'), list):
                log.info("Old state format detected. Migrating to new dictionary format.")
                migrated_down_services = {}
                for service_name in state['down_services']:
                    migrated_down_services[service_name] = {'failure_count': 1}
                state['down_services'] = migrated_down_services
                save_state(state) # Save the migrated state immediately

            if 'down_services' not in state or not isinstance(state['down_services'], dict):
                return default_state
            return state
            
    except (json.JSONDecodeError, IOError) as e:
        log.error(f"Could not read or parse state file at '{STATE_FILE_PATH}': {e}")
        return default_state

def save_state(state: Dict[str, Any]):
    """
    Saves the given state to the JSON file.

    Args:
        state (Dict[str, Any]): The current state dictionary to save.
    """
    try:
        with open(STATE_FILE_PATH, 'w') as f:
            json.dump(state, f, indent=4)
    except IOError as e:
        log.error(f"Could not write to state file at '{STATE_FILE_PATH}': {e}")

def is_service_down(service_name: str, state: Dict[str, Any]) -> bool:
    """Checks if a service is currently marked as down in the state."""
    return service_name in state.get('down_services', {})

def mark_service_down(service_name: str, state: Dict[str, Any]):
    """Marks a service as down in the state, initializing its failure count."""
    if not is_service_down(service_name, state):
        state.get('down_services', {})[service_name] = {'failure_count': 1}
        log.info(f"Marking service '{service_name}' as down.")

def mark_service_up(service_name: str, state: Dict[str, Any]):
    """Marks a service as up (removes it from the down list) in the state."""
    if is_service_down(service_name, state):
        del state.get('down_services', {})[service_name]
        log.info(f"Marking service '{service_name}' as up.")

def get_failure_count(service_name: str, state: Dict[str, Any]) -> int:
    """Gets the current failure count for a service."""
    return state.get('down_services', {}).get(service_name, {}).get('failure_count', 0)

def increment_failure_count(service_name: str, state: Dict[str, Any]):
    """Increments the failure count for a service. Marks it as down if not already."""
    if not is_service_down(service_name, state):
        mark_service_down(service_name, state)
    else:
        count = get_failure_count(service_name, state)
        state['down_services'][service_name]['failure_count'] = count + 1
    log.info(f"Incremented failure count for '{service_name}' to {get_failure_count(service_name, state)}.")

def reset_failure_count(service_name: str, state: Dict[str, Any]):
    """Resets the failure count for a service to 0 if it exists."""
    if is_service_down(service_name, state):
        state['down_services'][service_name]['failure_count'] = 0
        log.info(f"Reset failure count for '{service_name}'.")
