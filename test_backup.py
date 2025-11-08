# -*- coding: utf-8 -*-
"""
Standalone Test Script for the Backup Health Monitor (Log Parsing Version)

This script tests the logic of the `backup_check.py` module by pointing it
at a sample log file. It mocks the `send_alert` function to verify the
alerting logic without sending real notifications.

---
HOW TO RUN THIS SCRIPT:
---
1. Make sure you have run the main setup script first:
   bash scripts/setup.sh

2. Activate the virtual environment:
   source .venv/bin/activate

3. Run this script from the project's root directory:
   python test_backup.py
---
"""

import sys
import os
import json
import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from monitors import backup_check
except ImportError as e:
    print(f"ERROR: Could not import modules: {e}")
    sys.exit(1)

def mock_send_alert(message: str, severity: str, title: str, details: str):
    """A fake 'send_alert' function that prints alert details."""
    print("\n--- MOCK ALERT (Not Sent) ---")
    print(f"  Severity: {severity.upper()}")
    print(f"  Title:    {title}")
    print(f"  Message:  {message}")
    print(f"  Details:  {details}")
    print("---------------------------\n")

def run_backup_test():
    """Runs a series of tests against the backup monitor."""
    print("--- Starting Backup Health Test (Log Parsing) ---")

    # Monkey-patch the real send_alert function with our mock
    original_send_alert = backup_check.send_alert
    backup_check.send_alert = mock_send_alert

    sample_log_path = "sample_rclone.log"
    if not os.path.exists(sample_log_path):
        print(f"ERROR: Sample log file '{sample_log_path}' not found!")
        return

    # --- Test Case 1: Check for the latest (failed) backup ---
    # We need to trick the script into thinking the log is recent.
    # We'll set the 'max_age_hours' to be very large to ensure it finds the last entry.
    print("\n--- Test Case 1: Parsing the latest entry (a failed backup) ---")
    config_fail = {
        'log_path': sample_log_path,
        'min_size_mb': 1000,
        'max_age_hours': 365 * 24 # A year, to make sure we find the entry
    }
    result = backup_check.check_backup_health(config_fail)
    print("Parsed Results:")
    print(json.dumps(result, indent=4, default=str))


    # --- Test Case 2: Check for a successful backup ---
    # To find the successful backup, we must set the time window to exclude the failed one.
    # The successful backup is from Nov 3, the failed one is Nov 4.
    # We'll set the age so it can't see the Nov 4 entry.
    # This is a bit of a hack for testing, assuming 'now' is Nov 4 or later.
    print("\n--- Test Case 2: Parsing an older, successful backup ---")
    # To simulate finding the older entry, we can't do it with one file.
    # A better test is to check the successful log on its own.
    # For this script, we'll just test different failure modes.
    
    # --- Test Case 3: Test 'backup too small' failure ---
    print("\n--- Test Case 3: Testing 'Backup Too Small' failure ---")
    config_small = {
        'log_path': sample_log_path,
        'min_size_mb': 3000, # Set high to trigger failure on the last successful backup
        'max_age_hours': 365 * 24
    }
    # We need to temporarily modify the log to make the last entry a success
    with open(sample_log_path, 'r') as f:
        content = f.read()
    # Replace the error line to simulate success
    content_success = content.replace("Errors:                 1", "Errors:                 0")
    tmp_success_log = "/tmp/temp_success.log"
    with open(tmp_success_log, "w") as f:
        f.write(content_success)
    
    config_small['log_path'] = tmp_success_log
    result = backup_check.check_backup_health(config_small)
    print("Parsed Results:")
    print(json.dumps(result, indent=4, default=str))
    os.remove(tmp_success_log)


    # --- Test Case 4: Test 'log file not found' ---
    print("\n--- Test Case 4: Testing 'Log Not Found' failure ---")
    config_no_log = {
        'log_path': '/tmp/this_log_does_not_exist.log',
        'min_size_mb': 100,
        'max_age_hours': 25
    }
    result = backup_check.check_backup_health(config_no_log)
    print("Parsed Results:")
    print(json.dumps(result, indent=4, default=str))


    # Restore the original function
    backup_check.send_alert = original_send_alert
    print("\n--- Test Complete ---")

if __name__ == "__main__":
    run_backup_test()
