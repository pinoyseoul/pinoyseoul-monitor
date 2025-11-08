# -*- coding: utf-8 -*-
"""
Standalone Test Script for the Docker Health Monitor

This script tests the logic of the `docker_health.py` module without sending
any actual alerts to Google Chat. It does this by temporarily replacing
(or "mocking") the `send_alert` function with a fake one that just prints
the alert details to the console.

This allows you to safely test the container checking logic and see the
data structure that the function returns.

---
HOW TO RUN THIS SCRIPT:
---
1. Make sure you have run the main setup script first:
   bash scripts/setup.sh

2. Activate the virtual environment:
   source .venv/bin/activate

3. Run this script from the project's root directory:
   python test_docker.py
---
"""

import sys
import os
import json

# This ensures the script can find the 'monitors' and 'utils' modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    # Import the module we want to test
    from monitors import docker_health
except ImportError as e:
    print(f"ERROR: Could not import modules: {e}")
    print("Please ensure you have run 'bash scripts/setup.sh' and are running this script")
    print("from the root of the 'pinoyseoul-monitor' directory.")
    sys.exit(1)


def mock_send_alert(message: str, severity: str, title: str, details: str):
    """
    This is a fake 'send_alert' function. Instead of sending a real alert,
    it just prints the details of the alert it received to the console.
    """
    print("\n--- MOCK ALERT (Not Sent) ---")
    print(f"  Severity: {severity.upper()}")
    print(f"  Title:    {title}")
    print(f"  Message:  {message}")
    print(f"  Details:  \n{details}")
    print("---------------------------\n")


def run_docker_test():
    """
    Replaces the real alert function with our mock one, runs the docker
    health check, and prints the results.
    """
    print("--- Starting Docker Health Test (Alerts will be mocked) ---")

    # This is the key step: we replace the real function with our fake one.
    original_send_alert = docker_health.send_alert
    docker_health.send_alert = mock_send_alert

    # Define a mock name map, similar to what would be in config.yml
    mock_name_map = {
        "kimai": "Kimai Time Tracking",
        "portainer": "Portainer UI",
        "azuracast": "Radio Platform"
    }
    print(f"Using mock name map: {mock_name_map}")

    # Now, when check_docker_health runs, it will call our fake function
    results = docker_health.check_docker_health(name_map=mock_name_map)

    # It's good practice to restore the original function afterwards
    docker_health.send_alert = original_send_alert

    print("\n--- TEST COMPLETE ---")
    print("Health check logic finished. Any alerts that would have been sent were printed above.")
    print("\nFinal data structure returned by the function:")
    # Use json.dumps for pretty-printing the dictionary
    print(json.dumps(results, indent=4))
    print("---------------------\n")


if __name__ == "__main__":
    run_docker_test()
