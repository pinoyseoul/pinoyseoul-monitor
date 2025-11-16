#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A simple script to send a test message to the configured Google Chat webhook.
"""

import os
import sys
import logging

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from utils.google_chat import test_webhook
    from utils.logger import setup_logging
    from main import load_config
except ImportError as e:
    print(f"FATAL ERROR: A required module is missing: {e}", file=sys.stderr)
    print("Please run 'pip install -r requirements.txt' to install dependencies.", file=sys.stderr)
    sys.exit(1)

log = logging.getLogger(__name__)

if __name__ == "__main__":
    print("--- Sending Webhook Test Message ---")
    try:
        config = load_config()
        setup_logging(config.get('logging', {}))
        
        log.info("Running webhook test...")
        test_webhook()
        print("Test alert sent. Please check your Google Chat room.")
        print("------------------------------------")
    except SystemExit as e:
        # Config loading errors are handled in load_config, just exit
        sys.exit(e.code)
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)
