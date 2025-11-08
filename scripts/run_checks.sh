#!/bin/bash
#
# Cron Wrapper Script for PinoySeoul Monitor
#
# PURPOSE:
# This script acts as a safe and reliable entry point for running monitor
# checks from a cron job. It ensures the correct virtual environment is
# activated and runs the main Python script with the specified check.
#
# USAGE:
# Call this script from your crontab with the desired check as an argument.
#
# EXAMPLE CRON ENTRIES:
#
# # Run all checks every 15 minutes and log to a file
# */15 * * * * /bin/bash /path/to/run_checks.sh all >> /path/to/cron.log 2>&1
#
# # Run only the Docker check every 5 minutes
# */5 * * * * /bin/bash /path/to/run_checks.sh docker >> /path/to/cron.log 2>&1
#

# --- Configuration ---
set -e # Exit immediately if a command exits with a non-zero status.
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." &> /dev/null && pwd )"
VENV_DIR="$PROJECT_DIR/.venv"

# --- Argument Validation ---
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 [docker|ssl|backup|all]"
    echo "Error: You must provide exactly one check name as an argument."
    exit 1
fi

CHECK_NAME=$1

# --- Main Execution ---

# 1. Verify virtual environment exists
if [ ! -f "$VENV_DIR/bin/activate" ]; then
    echo "ERROR: Python virtual environment not found at '$VENV_DIR'."
    echo "Please run the setup script first: bash $PROJECT_DIR/scripts/setup.sh"
    exit 1
fi

# 2. Activate the virtual environment
source "$VENV_DIR/bin/activate"

# 3. Navigate to the project directory
cd "$PROJECT_DIR"

# 4. Run the main Python script with the provided argument
# The python script's internal logger will handle file-based logging.
# The cron job itself should handle redirecting stdout/stderr if desired.
echo "--- [$(date)] Running check: $CHECK_NAME ---"
python main.py --check "$CHECK_NAME"
echo "--- [$(date)] Check complete: $CHECK_NAME ---"

# 5. Deactivate the virtual environment
deactivate