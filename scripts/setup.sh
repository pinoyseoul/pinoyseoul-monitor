#!/bin/bash
#
# This script provides a guided, automated setup for the PinoySeoul Monitor.
# It prepares the environment, installs dependencies, creates configuration
# files, and verifies the setup by testing the webhook connection.
#

# --- Configuration & Style ---
set -e # Exit immediately if a command exits with a non-zero status.
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." &> /dev/null && pwd )"
VENV_DIR="$PROJECT_DIR/.venv"
PYTHON_EXEC="python3"
C_RESET='\033[0m'
C_GREEN='\033[0;32m'
C_YELLOW='\033[0;33m'
C_BOLD='\033[1m'

echo -e "${C_BOLD}--- Starting PinoySeoul Monitor Automated Setup ---${C_RESET}"
cd "$PROJECT_DIR"

# --- 1. Check for Python ---
echo -e "\n[1/6] Checking for Python 3..."
if ! command -v $PYTHON_EXEC &> /dev/null; then
    echo "ERROR: python3 is not installed or not in PATH. Please install Python 3.8 or higher."
    exit 1
fi
PY_VERSION=$($PYTHON_EXEC -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "✅ Found Python version $PY_VERSION."

# --- 2. Create Python Virtual Environment ---
echo -e "\n[2/6] Setting up Python virtual environment..."
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment in '$VENV_DIR'..."
    $PYTHON_EXEC -m venv "$VENV_DIR"
else
    echo "Virtual environment already exists. Skipping creation."
fi
echo "✅ Virtual environment is ready."

# --- 3. Install Dependencies ---
echo -e "\n[3/6] Installing required packages from requirements.txt..."
# Activate the virtual environment for the installation step
source "$VENV_DIR/bin/activate"
pip install --upgrade pip > /dev/null
pip install -r requirements.txt
deactivate
echo "✅ All dependencies installed."

# --- 4. Create Configuration Files ---
echo -e "\n[4/6] Creating configuration files..."
# Create config.yml from example if it doesn't exist
if [ ! -f "config.yml" ]; then
    echo "Copying 'config.example.yml' to 'config.yml'..."
    cp config.example.yml config.yml
else
    echo "'config.yml' already exists. Skipping."
fi
# Create .env from example if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Copying '.env.example' to '.env'..."
    cp .env.example .env
else
    echo "'.env' already exists. Skipping."
fi
echo "✅ Configuration files are in place."

# --- 5. Prompt for User Edits ---
echo -e "\n${C_YELLOW}[5/6] ${C_BOLD}USER ACTION REQUIRED${C_RESET}"
echo "Please edit the '.env' and 'config.yml' files with your actual values."
echo "Specifically, ensure ${C_BOLD}GOOGLE_CHAT_WEBHOOK_URL${C_RESET} in '.env' is correct."
read -p "Press [Enter] to continue after you have edited the files..."

# --- 6. Test Webhook Connection ---
echo -e "\n[6/6] Testing webhook connection..."
echo "This will run 'python main.py --test' to send a test message."
source "$VENV_DIR/bin/activate"
python main.py --test
deactivate
echo -e "\n${C_GREEN}✅ Webhook test complete. Please check your Google Chat room.${C_RESET}"

# --- Final Instructions ---
echo -e "\n${C_GREEN}${C_BOLD}--- SETUP COMPLETE! ---${C_RESET}"
echo "The monitoring system is now installed."
echo -e "\n${C_BOLD}Next Steps:${C_RESET}"
echo "1. To run a manual check, use the wrapper script:"
echo "   ${C_YELLOW}./scripts/run_checks.sh all${C_RESET}"
echo "2. To schedule checks, add the wrapper script to your crontab. For example, to run all checks every 15 minutes:"
echo "   ${C_YELLOW}*/15 * * * * /bin/bash $PROJECT_DIR/scripts/run_checks.sh all${C_RESET}"
echo ""