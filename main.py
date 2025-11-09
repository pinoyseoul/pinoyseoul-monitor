#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main entry point for the PinoySeoul Monitoring and Alerting Service.

This script provides a command-line interface to run various system health
checks, send summary reports, and test alert configurations.
"""

import argparse
import os
import sys
import yaml
import logging
from dotenv import load_dotenv
from datetime import datetime
import pytz

# --- Module Imports ---
# We wrap imports in a try/except block to provide a graceful exit
# if dependencies are not installed.
try:
    from utils.logger import setup_logging
    from utils.google_chat import send_daily_summary, test_webhook, send_alert
    from utils.quotes import get_random_quote
    from monitors.docker_health import check_docker_health
    from monitors.ssl_check import check_ssl_certs
    from monitors.backup_check import check_backup_age
    from monitors.azuracast_check import get_listener_summary
except ImportError as e:
    print(f"FATAL ERROR: A required module is missing: {e}", file=sys.stderr)
    print("Please run 'bash scripts/setup.sh' to install dependencies.", file=sys.stderr)
    sys.exit(1)

# --- Global Variables ---
log = logging.getLogger(__name__)

# --- Core Functions ---

def load_config(config_path: str = 'config.yml') -> dict:
    """
    Loads the YAML configuration file and substitutes environment variables.

    Args:
        config_path (str): The path to the configuration file.

    Returns:
        A dictionary containing the loaded and processed configuration.
    
    Raises:
        SystemExit: If the config file is not found or the webhook URL is missing.
    """
    log.info(f"Loading configuration from '{config_path}'...")
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        log.critical(f"Configuration file not found at '{config_path}'.")
        print(f"FATAL ERROR: Configuration file not found at '{config_path}'.", file=sys.stderr)
        print("Please copy 'config.example.yml' to 'config.yml' and configure it.", file=sys.stderr)
        sys.exit(1)

    # Load .env file for secrets
    load_dotenv()

    # Substitute environment variables in the config (e.g., for webhook_url)
    # This is a simple substitution for "${VAR_NAME}" format
    for section, settings in config.items():
        for key, value in settings.items():
            if isinstance(value, str) and value.startswith('${') and value.endswith('}'):
                var_name = value[2:-1]
                env_value = os.getenv(var_name)
                if not env_value:
                    log.critical(f"Environment variable '{var_name}' is not set, but is required for config key '{key}'.")
                    sys.exit(1)
                config[section][key] = env_value
    
    # Final validation
    if not config.get('google_chat', {}).get('webhook_url'):
        log.critical("GOOGLE_CHAT_WEBHOOK_URL is missing from config and environment.")
        sys.exit(1)
        
    log.info("Configuration loaded successfully.")
    return config

def run_summary(config: dict):
    """Runs all checks and sends a single daily summary report."""
    log.info("--- Starting Daily Summary Run ---")
    
    # Get configs for each module
    docker_config = config.get('docker', {})
    ssl_config = config.get('ssl', {})
    backup_config = config.get('backup', {})
    portainer_url = config.get('portainer', {}).get('url')
    nginx_proxy_manager_url = config.get('nginx_proxy_manager', {}).get('url')

    # Run all checks and collect results
    docker_results = check_docker_health(
        name_map=docker_config.get('container_name_mapping', {}),
        portainer_url=portainer_url
    )
    ssl_results = check_ssl_certs(
        domains=ssl_config.get('domains', []),
        alert_days=ssl_config.get('alert_days', {}),
        portainer_url=portainer_url,
        nginx_proxy_manager_url=nginx_proxy_manager_url
    )
    backup_results = check_backup_age(backup_config, portainer_url=portainer_url)

    # Format Docker status for summary
    docker_status = f"✅ {docker_results['running']}/{docker_results['total_containers']} containers running"
    if docker_results['status'] != 'healthy':
        docker_status = f"🔴 {len(docker_results['issues'])} issues detected"

    # Format SSL status for summary
    expiring_soon = [res for res in ssl_results if res['status'] in ['warning', 'critical']]
    ssl_status = f"✅ All {len(ssl_results)} certs valid"
    if expiring_soon:
        ssl_status = f"🟡 {len(expiring_soon)} certs require attention"

    # Format backup status for summary
    backup_status = f"✅ {backup_results.get('message', 'Status unknown')}"
    if backup_results['status'] != 'success':
        backup_status = f"🔴 {backup_results.get('message', 'Backup failed')}"

    # Mock data for services not yet implemented in detail
    services_status = {
        "Radio": "✅ Online", "Website": "✅ Online", "Kimai": "✅ Online",
        "Wekan": "✅ Online", "DocuSeal": "✅ Online", "Dolibarr": "✅ Online",
    }

    # Get a random morning quote
    morning_quote = get_random_quote('morning')

    send_daily_summary(services_status, backup_status, ssl_status, morning_quote)
    log.info("--- Daily Summary Sent ---")

def run_checks(check_name: str, config: dict) -> bool:
    """
    Runs a specific check or all checks.

    Args:
        check_name (str): The name of the check to run ('docker', 'ssl', 'backup', 'all').
        config (dict): The application configuration.

    Returns:
        bool: True if all checks passed, False if any issues were found.
    """
    log.info(f"--- Running Check: {check_name.upper()} ---")
    overall_healthy = True

    portainer_url = config.get('portainer', {}).get('url')
    nginx_proxy_manager_url = config.get('nginx_proxy_manager', {}).get('url')

    if check_name in ['docker', 'all']:
        docker_config = config.get('docker', {})
        if docker_config.get('enabled', False):
            results = check_docker_health(
                name_map=docker_config.get('container_name_mapping', {}),
                portainer_url=portainer_url
            )
            if results['status'] != 'healthy':
                overall_healthy = False
        else:
            log.info("Docker check skipped (disabled in config).")

    if check_name in ['ssl', 'all']:
        ssl_config = config.get('ssl', {})
        if ssl_config.get('enabled', False):
            results = check_ssl_certs(
                domains=ssl_config.get('domains', []),
                alert_days=ssl_config.get('alert_days', {}),
                portainer_url=portainer_url,
                nginx_proxy_manager_url=nginx_proxy_manager_url
            )
            if any(r['status'] != 'valid' for r in results):
                overall_healthy = False
        else:
            log.info("SSL check skipped (disabled in config).")

    if check_name in ['backup', 'all']:
        if config.get('backup', {}).get('enabled', False):
            results = check_backup_age(config.get('backup', {}), portainer_url=portainer_url)
            if results['status'] != 'success':
                overall_healthy = False
        else:
            log.info("Backup check skipped (disabled in config).")
            
    log.info(f"--- Check '{check_name.upper()}' Complete. Overall Healthy: {overall_healthy} ---")
    return overall_healthy

# --- Main Execution ---

def main():
    """The main function and entry point of the application."""
    parser = argparse.ArgumentParser(description="PinoySeoul Monitoring and Alerting Service.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--check', choices=['docker', 'ssl', 'backup', 'all'], help="Run a specific health check.")
    group.add_argument('--summary', action='store_true', help="Run all checks and send the daily summary report.")
    group.add_argument('--scheduled-summary', action='store_true', help="Run the daily summary only if it's the scheduled time.")
    group.add_argument('--listener-summary', action='store_true', help="Send the AzuraCast daily listener summary.")
    group.add_argument('--test', action='store_true', help="Send a test alert to the configured webhook.")
    
    args = parser.parse_args()

    try:
        config = load_config()
        setup_logging(config.get('logging', {}))
    except SystemExit as e:
        # load_config handles its own error printing
        sys.exit(e.code)
    except Exception as e:
        print(f"FATAL ERROR during initialization: {e}", file=sys.stderr)
        sys.exit(1)

    if args.test:
        log.info("Running webhook test...")
        test_webhook()
        print("Test alert sent. Please check your Google Chat room.")
        sys.exit(0)

    if args.listener_summary:
        log.info("Running AzuraCast listener summary...")
        azuracast_config = config.get('azuracast', {})
        if azuracast_config.get('enabled', False):
            # Get a random evening quote
            evening_quote = get_random_quote('evening')
            get_listener_summary(azuracast_config, evening_quote)
        else:
            log.warning("Azuracast check skipped (disabled in config).")
        sys.exit(0)

    if args.summary:
        run_summary(config)
        sys.exit(0)

    if args.scheduled_summary:
        tz_str = config.get('general', {}).get('timezone', 'UTC')
        summary_time_str = config.get('schedule', {}).get('daily_summary_time', '09:00')
        
        try:
            timezone = pytz.timezone(tz_str)
            now = datetime.now(timezone)
            
            summary_hour, summary_minute = map(int, summary_time_str.split(':'))
            
            # Check if the current time is within a 5-minute window of the scheduled time
            # This handles minor cron job delays
            if now.hour == summary_hour and now.minute >= summary_minute and now.minute < summary_minute + 5:
                log.info(f"Current time {now.strftime('%H:%M')} matches scheduled summary time {summary_time_str}. Running summary.")
                run_summary(config)
            else:
                log.info(f"Current time {now.strftime('%H:%M')} in {tz_str} is not the scheduled summary time ({summary_time_str}). Skipping.")
        except pytz.UnknownTimeZoneError:
            log.error(f"Invalid timezone '{tz_str}' in config. Skipping scheduled summary.")
            sys.exit(1)
        except Exception as e:
            log.error(f"An error occurred during scheduled summary check: {e}")
            sys.exit(1)
        sys.exit(0)

    if args.check:
        is_healthy = run_checks(args.check, config)
        if not is_healthy:
            log.warning(f"Check '{args.check}' completed with issues.")
            sys.exit(1) # Exit with error code if issues were found
        else:
            log.info(f"Check '{args.check}' completed successfully.")
            sys.exit(0)

if __name__ == "__main__":
    main()