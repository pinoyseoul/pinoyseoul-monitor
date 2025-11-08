# -*- coding: utf-8 -*-
"""
This module sets up an advanced logger for the application, with support for
console output, file rotation, and configurable log levels.
"""

import logging
import os
from logging.handlers import TimedRotatingFileHandler
from typing import Dict, Any

def setup_logging(config: Dict[str, Any]):
    """
    Configures the root logger based on the provided configuration.

    Args:
        config (Dict[str, Any]): A dictionary containing logging settings,
                                  e.g., {'level': 'INFO', 'log_dir': './logs', 'max_days': 7}
    """
    log_level = config.get('level', 'INFO').upper()
    log_dir = config.get('log_dir', './logs')
    max_days = config.get('max_days', 7)

    # Ensure the log directory exists
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, 'monitor.log')

    # Get the root logger
    logger = logging.getLogger()
    logger.setLevel(log_level)

    # Clear existing handlers to avoid duplication
    if logger.hasHandlers():
        logger.handlers.clear()

    # Create a formatter
    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 1. Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 2. Rotating File Handler
    # This handler rotates the log file daily and keeps a backup for 'max_days'.
    file_handler = TimedRotatingFileHandler(
        log_file,
        when='D',           # 'D' for daily rotation
        interval=1,         # Rotate every 1 day
        backupCount=max_days
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    logging.info("Logging configured successfully.")
    logging.info(f"Log level set to {log_level}. Logging to console and {log_file}.")

# You can get a logger instance in other modules by just calling:
# import logging
# log = logging.getLogger(__name__)