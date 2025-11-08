# -*- coding: utf-8 -*-
"""
Standalone Webhook Test Script for PinoySeoul Monitor

This script sends one of each alert type (CRITICAL, WARNING, INFO) to the
Google Chat webhook configured in your .env file. It's a simple way to
verify that your webhook URL is correct and that the message formatting works
as expected, without running the full monitoring application.

---
HOW TO RUN THIS SCRIPT:
---
1. Make sure you have run the main setup script first:
   bash scripts/setup.sh

2. Activate the virtual environment:
   source .venv/bin/activate

3. Run this script from the project's root directory:
   python test_webhook.py
---
"""

import os
import sys
import time
from dotenv import load_dotenv

# This ensures the script can find the 'utils' module when run from the root directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from utils.google_chat import send_alert
except ImportError:
    print("ERROR: Could not import 'send_alert'.")
    print("Please ensure you have run 'bash scripts/setup.sh' and are running this script")
    print("from the root of the 'pinoyseoul-monitor' directory.")
    sys.exit(1)

def run_tests():
    """
    Loads the environment and sends a sequence of test alerts.
    """
    # 1. Load the .env file to get the webhook URL
    load_dotenv()
    webhook_url = os.getenv("GOOGLE_CHAT_WEBHOOK_URL")

    if not webhook_url or webhook_url == "YOUR_GOOGLE_CHAT_WEBHOOK_URL_HERE":
        print("🔴 FAILURE: 'GOOGLE_CHAT_WEBHOOK_URL' not found in .env file.")
        print("Please ensure your .env file is correctly configured.")
        return

    print("--- Starting Webhook Test ---")
    print(f"Webhook URL found. Sending alerts...\n")

    # 2. Send a CRITICAL alert
    print("Sending CRITICAL alert...")
    try:
        send_alert(
            message="The main radio stream is offline.",
            severity="critical",
            title="Test: Radio Service Down",
            details="This is a test of a CRITICAL alert. No actual services are affected."
        )
        print("🟢 SUCCESS: CRITICAL alert sent.\n")
    except Exception as e:
        print(f"🔴 FAILURE: An error occurred while sending the CRITICAL alert: {e}\n")

    time.sleep(3) # Wait a few seconds to avoid flooding the chat room

    # 3. Send a WARNING alert
    print("Sending WARNING alert...")
    try:
        send_alert(
            message="High CPU usage detected on the database.",
            severity="warning",
            title="Test: Database Performance Degrading",
            details="This is a test of a WARNING alert. The system is still operational."
        )
        print("🟢 SUCCESS: WARNING alert sent.\n")
    except Exception as e:
        print(f"🔴 FAILURE: An error occurred while sending the WARNING alert: {e}\n")

    time.sleep(3)

    # 4. Send an INFO alert
    print("Sending INFO alert...")
    try:
        send_alert(
            message="A new version of the Kimai container has been deployed.",
            severity="info",
            title="Test: Service Update",
            details="This is a test of an INFO alert. This is for your information only."
        )
        print("🟢 SUCCESS: INFO alert sent.\n")
    except Exception as e:
        print(f"🔴 FAILURE: An error occurred while sending the INFO alert: {e}\n")

    print("--- Webhook Test Complete ---")
    print("Please check your Google Chat room to verify the messages were received.")


if __name__ == "__main__":
    run_tests()
