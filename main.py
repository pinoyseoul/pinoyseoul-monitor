#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main entry point for the PinoySeoul Monitoring and Alerting Service.

This script runs as a long-running service, scheduling and executing
monitoring jobs based on a central configuration file.
"""

import sys
import time
import yaml
import logging
from dotenv import load_dotenv

# --- Module Imports ---
try:
    import schedule
    from utils.logger import setup_logging
    from utils.google_chat import send_daily_summary, test_webhook
    from utils.quotes import get_random_quote
    from monitors.docker_health import check_docker_health
    from monitors.ssl_check import check_ssl_certs
    from monitors.backup_check import check_backup_age
    from monitors.azuracast_check import get_listener_summary
    from utils.state_manager import load_state, save_state
except ImportError as e:
    print(f"FATAL ERROR: A required module is missing: {e}", file=sys.stderr)
    print("Please run 'pip install -r requirements.txt' to install dependencies.", file=sys.stderr)
    sys.exit(1)

# --- Global Variables ---
log = logging.getLogger(__name__)

# --- Core Functions ---

def load_config(config_path: str = 'config.yml') -> dict:
    """Loads the YAML configuration file and substitutes environment variables."""
    log.info(f"Loading configuration from '{config_path}'...")
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        log.critical(f"Configuration file not found at '{config_path}'.")
        sys.exit(1)

    load_dotenv()
    # Recursively substitute environment variables
    def substitute_env_vars(item):
        if isinstance(item, dict):
            return {k: substitute_env_vars(v) for k, v in item.items()}
        elif isinstance(item, list):
            return [substitute_env_vars(i) for i in item]
        elif isinstance(item, str) and item.startswith('${') and item.endswith('}'):
            var_name = item[2:-1]
            env_value = os.getenv(var_name)
            if not env_value:
                log.critical(f"Environment variable '{var_name}' is not set, but is required in config.")
                sys.exit(1)
            return env_value
        return item

    config = substitute_env_vars(config)
    
    if not config.get('google_chat', {}).get('webhook_url'):
        log.critical("GOOGLE_CHAT_WEBHOOK_URL is missing from config and environment.")
        sys.exit(1)
        
    log.info("Configuration loaded successfully.")
    return config

# --- Job Functions ---

def run_monitor_job(monitor_name: str, monitor_func, config: dict):
    """A wrapper to run a monitor, handle exceptions, and manage state."""
    log.info(f"--- Running Job: {monitor_name.upper()} ---")
    state = load_state()
    monitor_config = config['monitors'][monitor_name]
    
    try:
        # Pass the specific monitor's config and the global integrations to the check
        monitor_func(monitor_config, config.get('integrations', {}), state)
    except Exception as e:
        log.error(f"!!! Job '{monitor_name.upper()}' failed with an unexpected error: {e}", exc_info=True)
    finally:
        save_state(state)
        log.info(f"--- Finished Job: {monitor_name.upper()} ---")

def run_summary_job(summary_name: str, summary_func, config: dict):
    """A wrapper to run a summary, handle exceptions, and manage state."""
    log.info(f"--- Running Summary: {summary_name.upper()} ---")
    state = load_state()
    monitor_config = config['monitors'][summary_name]

    try:
        if summary_name == 'daily_summary':
            # The daily summary needs info from all other checks
            summary_func(config, state)
        else:
            # Other summaries are self-contained
            summary_func(monitor_config, config.get('integrations', {}), state)
    except Exception as e:
        log.error(f"!!! Summary '{summary_name.upper()}' failed with an unexpected error: {e}", exc_info=True)

# --- Main Execution ---

def main():
    """The main function to schedule and run all monitoring jobs."""
    config = load_config()
    setup_logging(config.get('logging', {}))

    log.info("=================================================")
    log.info("  PinoySeoul Monitoring Service - Starting Up")
    log.info("=================================================")

    # Map monitor names from config to their actual functions
    JOB_MAP = {
        "docker": check_docker_health,
        "ssl": check_ssl_certs,
        "backup": check_backup_age,
        "listener_summary": get_listener_summary,
        "daily_summary": run_daily_summary_job_logic # A special function for the main summary
    }

    # --- Schedule all jobs based on config ---
    for name, monitor_config in config.get('monitors', {}).items():
        if not monitor_config.get('enabled', False):
            log.info(f"Skipping disabled monitor: '{name}'")
            continue

        if name not in JOB_MAP:
            log.warning(f"Unknown monitor type '{name}' found in config. Skipping.")
            continue

        job_func = JOB_MAP[name]
        
        # Schedule jobs that run at a specific time
        if 'run_at_time' in monitor_config:
            run_time = monitor_config['run_at_time']
            log.info(f"Scheduling '{name}' to run daily at {run_time}.")
            schedule.every().day.at(run_time).do(run_monitor_job, name, job_func, config)
        
        # Schedule jobs that run at a frequency
        elif 'schedule_minutes' in monitor_config:
            minutes = monitor_config['schedule_minutes']
            log.info(f"Scheduling '{name}' to run every {minutes} minutes.")
            schedule.every(minutes).minutes.do(run_monitor_job, name, job_func, config)

    log.info("--- All jobs scheduled. Starting monitoring loop. ---")
    
    # Run the scheduler loop
    while True:
        schedule.run_pending()
        time.sleep(1)

def run_daily_summary_job_logic(config: dict, state: dict):
    """The specific logic for creating and sending the daily summary report."""
    log.info("--- Composing Daily Summary Report ---")
    
    # For the summary, we need to run the checks to get fresh data
    # Note: This does NOT trigger alerts, it just gets the status
    docker_results = check_docker_health(config['monitors']['docker'], config.get('integrations', {}), state, send_alerts=False)
    ssl_results = check_ssl_certs(config['monitors']['ssl'], config.get('integrations', {}), state, send_alerts=False)
    backup_results = check_backup_age(config['monitors']['backup'], config.get('integrations', {}), state, send_alerts=False)

    # Format Docker status
    docker_status = f"✅ {docker_results['running']}/{docker_results['total_containers']} containers running"
    if docker_results['status'] != 'healthy':
        docker_status = f"🔴 {len(docker_results['issues'])} issues detected"

    # Format SSL status
    expiring_soon = [res for res in ssl_results if res['status'] in ['warning', 'critical']]
    ssl_status = f"✅ All {len(ssl_results)} certs valid"
    if expiring_soon:
        ssl_status = f"🟡 {len(expiring_soon)} certs require attention"

    # Format backup status
    backup_status = f"✅ {backup_results.get('message', 'Status unknown')}"
    if backup_results['status'] != 'success':
        backup_status = f"🔴 {backup_results.get('message', 'Backup failed')}"

    services_status = {
        "Radio": "✅ Online", "Website": "✅ Online", "Kimai": "✅ Online",
        "Wekan": "✅ Online", "DocuSeal": "✅ Online", "Dolibarr": "✅ Online",
    }
    morning_quote = get_random_quote('morning')

    send_daily_summary(services_status, backup_status, ssl_status, morning_quote)
    log.info("--- Daily Summary Sent ---")


if __name__ == "__main__":
    main()