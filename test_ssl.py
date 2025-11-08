# -*- coding: utf-8 -*-
"""
Standalone Test Script for the SSL Certificate Monitor

This script tests the logic of the `ssl_check.py` module without sending
any actual alerts to Google Chat. It does this by temporarily replacing
(or "mocking") the `send_alert` function with a fake one that just prints
the alert details to the console.

This allows you to safely verify the SSL check logic, certificate date parsing,
and expiry calculations.

---
HOW TO RUN THIS SCRIPT:
---
1. Make sure you have run the main setup script first:
   bash scripts/setup.sh

2. Activate the virtual environment:
   source .venv/bin/activate

3. Run this script from the project's root directory:
   python test_ssl.py
---
"""

import sys
import os
import json

# This ensures the script can find the 'monitors' and 'utils' modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    # Import the module we want to test
    from monitors import ssl_check
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
    print("---------------------------\n")


def run_ssl_test():
    """
    Replaces the real alert function with our mock one, runs the SSL
    health check, and prints the results.
    """
    print("--- Starting SSL Certificate Test (Alerts will be mocked) ---")

    # This is the key step: we replace the real function with our fake one.
    original_send_alert = ssl_check.send_alert
    ssl_check.send_alert = mock_send_alert

    domains_to_test = [
        "google.com",           # Known good
        "expired.badssl.com",   # Known expired
        "radio.pinoyseoul.com"  # Your real domain
    ]
    print(f"Domains to be checked: {domains_to_test}")

    # Define a mock alert days config, similar to what would be in config.yml
    mock_alert_days = {
        'critical': 7,
        'warning': 30
    }
    print(f"Using mock alert thresholds: {mock_alert_days}\n")

    # Now, when check_ssl_certs runs, it will call our fake function
    results = ssl_check.check_ssl_certs(domains_to_test, alert_days=mock_alert_days)

    # It's good practice to restore the original function afterwards
    ssl_check.send_alert = original_send_alert

    print("\n--- TEST COMPLETE ---")
    print("SSL check logic finished. Any alerts that would have been sent were printed above.")
    
    print("\n--- Individual Results ---")
    for res in results:
        domain = res['domain']
        status = res['status'].upper()
        days = res['days_until_expiry']
        
        if status == 'VALID':
            print(f"✅ {domain}: VALID for {days} days.")
        elif status == 'ERROR':
            print(f"❌ {domain}: ERROR - Could not be reached.")
        else:
            # For WARNING or CRITICAL statuses
            if days < 0:
                print(f"🔴 {domain}: CRITICAL - EXPIRED {-days} days ago.")
            else:
                print(f"🟡 {domain}: {status} - Expires in {days} days.")

    print("\nFinal data structure returned by the function:")
    print(json.dumps(results, indent=4))
    print("---------------------\n")


if __name__ == "__main__":
    run_ssl_test()
