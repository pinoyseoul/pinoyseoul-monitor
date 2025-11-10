#!/bin/bash
#
# Cron Wrapper Script for PinoySeoul Monitor Summaries
#
# PURPOSE:
# This script acts as a safe and reliable entry point for running summary
# tasks from a cron job. It ensures the correct virtual environment is
# activated and runs the main Python script with the specified summary command.
#
# USAGE:
# Call this script from your crontab with the desired summary type as an argument.
#
# EXAMPLE CRON ENTRIES:
#
# # Send the daily summary report every day at 9:00 AM
# 0 9 * * * /bin/bash /path/to/run_summary.sh summary >> /path/to/cron.log 2>&1
#
# # Send the listener summary report every day at 9:00 PM
# 0 21 * * * /bin/bash /path/to/run_summary.sh listener-summary >> /path/to/cron.log 2>&1

# --- Configuration ---
set -e # Exit immediately if a command exits with a non-zero status.
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." &> /dev/null && pwd )"
VENV_DIR="$PROJECT_DIR/.venv"

# --- Argument Validation ---
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 [summary|listener-summary]"
    echo "Error: You must provide exactly one summary type as an argument."
    exit 1
fi

SUMMARY_TYPE=$1

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
echo "--- [$(date)] Running summary: $SUMMARY_TYPE ---"
if [ "$SUMMARY_TYPE" == "summary" ]; then
    python main.py --scheduled-summary
elif [ "$SUMMARY_TYPE" == "listener-summary" ]; then
    python main.py --scheduled-listener-summary
else
    echo "Error: Invalid summary type '$SUMMARY_TYPE'. Use 'summary' or 'listener-summary'."
    exit 1
fi
echo "--- [$(date)] Summary complete: $SUMMARY_TYPE ---"

# 5. Deactivate the virtual environment
deactivate
