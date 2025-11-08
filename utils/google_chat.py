# -*- coding: utf-8 -*-
"""
This module handles the formatting and sending of messages to Google Chat
using webhooks. It is designed to create rich, formatted cards for different
alert severities and daily summaries, tailored to the PinoySeoul Media brand.
"""

import os
import time
import requests
from datetime import datetime
from typing import Dict, Any, Optional, List
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up a logger for this module
log = logging.getLogger(__name__)

# Get Portainer URL from environment variable, with a fallback for safety
PORTAINER_URL = os.getenv("PORTAINER_URL", "http://localhost:9000")

# --- Private Helper Functions ---

def _get_webhook_url() -> Optional[str]:
    """Retrieves and validates the Google Chat webhook URL from environment variables."""
    webhook_url = os.getenv("GOOGLE_CHAT_WEBHOOK_URL")
    if not webhook_url or webhook_url == "YOUR_GOOGLE_CHAT_WEBHOOK_URL_HERE":
        log.error("Google Chat webhook URL is not configured. Skipping notification.")
        return None
    return webhook_url

def _send_card(card_payload: Dict[str, Any]) -> bool:
    """
    Sends a card-based message to the configured Google Chat webhook with a retry mechanism.

    Args:
        card_payload (Dict[str, Any]): The fully constructed Google Chat card payload.

    Returns:
        bool: True if the message was sent successfully, False otherwise.
    """
    webhook_url = _get_webhook_url()
    if not webhook_url:
        return False

    max_retries = 2
    for attempt in range(max_retries):
        try:
            response = requests.post(webhook_url, json=card_payload, timeout=15)
            response.raise_for_status()
            log.info(f"Successfully sent message to Google Chat on attempt {attempt + 1}.")
            return True
        except requests.exceptions.RequestException as e:
            log.error(f"Attempt {attempt + 1} failed to send message to Google Chat: {e}")
            if attempt < max_retries - 1:
                log.info("Retrying in 5 seconds...")
                time.sleep(5)
            else:
                log.error("All retry attempts failed.")
                return False
    return False

# --- Public API Functions ---

def send_alert(message: str, severity: str = "info", title: Optional[str] = None, details: Optional[str] = None):
    """
    Sends a severity-based alert to Google Chat.

    Args:
        message (str): The primary, user-facing message explaining the event.
        severity (str, optional): The severity level ("critical", "warning", "info").
                                  Defaults to "info".
        title (str, optional): The main title for the alert card.
        details (str, optional): Additional non-technical details about the impact or
                                 remediation steps.
    """
    log.info(f"Preparing alert with severity '{severity}': {title} - {message}")

    severity_styles = {
        "critical": {"icon": "🔴", "color": "#FF0000", "header": "IMMEDIATE ATTENTION REQUIRED"},
        "warning": {"icon": "🟡", "color": "#FFBF00", "header": "SYSTEM WARNING"},
        "info": {"icon": "🟢", "color": "#36A64F", "header": "SYSTEM UPDATE"},
    }
    style = severity_styles.get(severity, severity_styles["info"])

    card_header = {
        "title": f"{style['icon']} {style['header']}",
        "subtitle": title or "Platform Notification",
        "imageUrl": "https://img.icons8.com/fluency/96/sound-wave-apm.png",
        "imageType": "CIRCLE"
    }

    widgets = [{"textParagraph": {"text": f"<b>{message}</b>"}}]
    if details:
        widgets.append({"textParagraph": {"text": details}})

    # Add timestamp and action button
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z")
    widgets.extend([
        {"textParagraph": {"text": f"<i><font color='#7F7F7F'>Timestamp: {timestamp}</font></i>"}},
        {
            "buttonList": {
                "buttons": [
                    {
                        "text": "View in Portainer",
                        "onClick": {"openLink": {"url": PORTAINER_URL}}
                    }
                ]
            }
        }
    ])

    card_payload = {
        "cardsV2": [{
            "cardId": "alert-card",
            "card": {
                "header": card_header,
                "sections": [{"widgets": widgets}]
            }
        }]
    }

    _send_card(card_payload)

def send_daily_summary(services_status: Dict[str, str], backup_status: str, ssl_status: str):
    """
    Sends a structured daily summary report to Google Chat.

    Args:
        services_status (Dict[str, str]): A dictionary mapping service names to their status.
        backup_status (str): A summary string for the backup status.
        ssl_status (str): A summary string for the SSL certificate status.
    """
    log.info("Preparing daily summary report.")
    date_str = datetime.now().strftime("%B %d, %Y")

    # Dynamically build the service status text
    tools_status_lines = [
        f"• Kimai: {services_status.get('Kimai', 'Unknown')}",
        f"• Wekan: {services_status.get('Wekan', 'Unknown')}",
        f"• DocuSeal: {services_status.get('DocuSeal', 'Unknown')}",
        f"• Dolibarr: {services_status.get('Dolibarr', 'Unknown')}",
    ]
    tools_status_text = "<br>".join(tools_status_lines)

    summary_text = (
        f"✅ <b>All systems operational</b><br>"
        f"Radio: {services_status.get('Radio', 'Unknown')}<br>"
        f"Website: {services_status.get('Website', 'Unknown')}<br><br>"
        f"<b>Team Tools:</b><br>{tools_status_text}<br><br>"
        f"<b>Backups:</b> {backup_status}<br>"
        f"<b>SSL Certs:</b> {ssl_status}<br><br>"
        "<i>Have a productive day! 🚀</i>"
    )

    card_payload = {
        "cardsV2": [{
            "cardId": "summary-card",
            "card": {
                "header": {
                    "title": f"📊 PinoySeoul Daily Status - {date_str}",
                    "imageUrl": "https://img.icons8.com/fluency/96/positive-dynamic.png",
                    "imageType": "CIRCLE"
                },
                "sections": [{
                    "widgets": [{"textParagraph": {"text": summary_text}}]
                }]
            }
        }]
    }
    _send_card(card_payload)

def test_webhook():
    """
    Sends a simple test message to the configured webhook to verify connectivity.
    """
    log.info("Sending a test message to verify webhook configuration...")
    card_payload = {
        "cardsV2": [{
            "cardId": "test-card",
            "card": {
                "header": {"title": "Webhook Test Successful!"},
                "sections": [{
                    "widgets": [{
                        "textParagraph": {
                            "text": "If you can see this message, your `GOOGLE_CHAT_WEBHOOK_URL` is configured correctly."
                        }
                    }]
                }]
            }
        }]
    }
    success = _send_card(card_payload)
    if success:
        log.info("Test message sent successfully.")
    else:
        log.error("Failed to send test message. Please check your webhook URL and network connection.")

if __name__ == '__main__':
    print("--- Running PinoySeoul Google Chat Module Tests ---")

    # 1. Test basic webhook connectivity
    test_webhook()
    print("\n")
    time.sleep(2)

    # 2. Test 'critical' alert
    print("Testing CRITICAL alert...")
    send_alert(
        message="Listeners can't access the stream.",
        severity="critical",
        title="Radio Platform Offline",
        details="Impact: This is a P0 issue affecting all listeners. Nash has been notified via PagerDuty."
    )
    print("\n")
    time.sleep(2)

    # 3. Test 'warning' alert
    print("Testing WARNING alert...")
    send_alert(
        message="High memory usage detected.",
        severity="warning",
        title="Kimai Slower Than Usual",
        details="Impact: Time tracking may be slow. Monitoring resource usage for the next hour. No action needed from the team at this time."
    )
    print("\n")
    time.sleep(2)

    # 4. Test 'info' alert
    print("Testing INFO alert...")
    send_alert(
        message="2.3 GB backed up to Google Drive.",
        severity="info",
        title="Backup Completed Successfully"
    )
    print("\n")
    time.sleep(2)

    # 5. Test daily summary
    print("Testing DAILY SUMMARY...")
    mock_services = {
        "Radio": "✅ Online | 128 listeners, 1,400 songs played",
        "Website": "✅ Online",
        "Kimai": "✅ Online",
        "Wekan": "✅ Online",
        "DocuSeal": "✅ Online",
        "Dolibarr": "✅ Online",
    }
    mock_backup = "✅ Successful (3.1 GB)"
    mock_ssl = "✅ All certs valid for 60+ days"
    send_daily_summary(mock_services, mock_backup, mock_ssl)

    print("\n--- All tests complete. Please check your Google Chat room. ---")