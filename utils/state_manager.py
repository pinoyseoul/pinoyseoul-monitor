# -*- coding: utf-8 -*-
"""
Manages the state of the monitoring system, allowing it to remember
the status of services between checks.
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
    """
    default_state = {'down_services': []}
    if not os.path.exists(STATE_FILE_PATH):
        return default_state
    
    try:
        with open(STATE_FILE_PATH, 'r') as f:
            state = json.load(f)
            # Ensure the required keys exist
            if 'down_services' not in state:
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
    return service_name in state.get('down_services', [])

def mark_service_down(service_name: str, state: Dict[str, Any]):
    """Marks a service as down in the state."""
    if not is_service_down(service_name, state):
        state.get('down_services', []).append(service_name)
        log.info(f"Marking service '{service_name}' as down.")

def mark_service_up(service_name: str, state: Dict[str, Any]):
    """Marks a service as up (removes it from the down list) in the state."""
    if is_service_down(service_name, state):
        state.get('down_services', []).remove(service_name)
        log.info(f"Marking service '{service_name}' as up.")
