# PinoySeoul Monitor: Detailed Setup Guide

This guide provides a comprehensive, step-by-step walkthrough for installing, configuring, and verifying the PinoySeoul Monitoring Service on a new server.

---

## ✅ Prerequisites Checklist

Before you begin, ensure your server environment meets the following requirements.

| Requirement | Command to Verify | Notes |
| :--- | :--- | :--- |
| **Ubuntu Server** | `lsb_release -a` | Recommended: 22.04 LTS |
| **SSH Access** | `ssh your_user@your_server_ip` | You need sudo privileges. |
| **Python 3.8+** | `python3 --version` | Required to run the application. |
| **Python Venv** | `dpkg -s python3.10-venv` | If not installed, run `sudo apt install python3.10-venv`. |
| **Git** | `git --version` | Required to clone the repository. |
| **Docker** | `docker --version` | The Docker daemon must be running. |
| **Google Chat Room**| - | A space where you can add a webhook. |

---

## ⚙️ Step 1: Clone the Repository

First, connect to your server via SSH and clone the project repository into the desired directory.

```bash
# Navigate to your home directory
cd ~

# Clone the project
git clone <your-repository-url> pinoyseoul-monitor

# Enter the project directory
cd pinoyseoul-monitor
```
> **Troubleshooting:**
> - **Error: `git: command not found`**: Git is not installed. Run `sudo apt update && sudo apt install git`.
> - **Error: `Permission denied (publickey)`**: Your SSH key is not authorized on the server. Ensure your public key is in `~/.ssh/authorized_keys`.

---

## 🚀 Step 2: Run the Automated Setup Script

The `setup.sh` script is designed to automate the entire installation process.

```bash
bash scripts/setup.sh
```

This script performs the following actions:
1.  **Checks for Python:** Verifies that `python3` is installed.
2.  **Creates Virtual Environment:** Creates a self-contained Python environment in the `.venv/` directory.
3.  **Installs Dependencies:** Installs all required Python packages from `requirements.txt`.
4.  **Creates Config Files:** Copies `config.example.yml` to `config.yml` and `.env.example` to `.env` if they don't already exist.

> **Troubleshooting:**
> - **Error: `virtual environment was not created successfully`**: The `python3-venv` package is likely missing. Run `sudo apt install python3.10-venv` and then re-run the setup script.
> - **Error: `pip: command not found` or package installation fails**: Your Python installation may be broken, or you may have network issues preventing downloads from PyPI.

---

## 📝 Step 3: Configure the Monitor

The setup script will pause and prompt you to edit your configuration files. This is the most important manual step.

### 3.1 - Configure `.env` (Secrets)
Open the `.env` file with a text editor (like `nano` or `vim`).

```bash
nano .env
```

You will see one line. Replace `your_webhook_url_here` with the actual webhook URL you generated from Google Chat.

> [TODO: Add screenshot of a configured .env file]

### 3.2 - Configure `config.yml` (Settings)
Open the `config.yml` file.

```bash
nano config.yml
```
Review every section to ensure it matches your environment:
- **`docker.container_name_mapping`**: Verify that the container names on the left (e.g., `azuracast`, `kimai`) exactly match the names you see when you run `docker ps`.
- **`ssl.domains`**: Ensure this list includes every public domain and subdomain you want to monitor.
- **`backup.log_path`**: Double-check that this is the correct absolute path to the `rclone` log file created by your `backup.sh` script.
- **`backup.min_size_mb`**: Adjust this value to a reasonable minimum size for your backups. If your daily backup is usually 2.5 GB, a good minimum might be `1500` (1.5 GB).
- **`portainer.url`**: Make sure this is the correct public URL for your Portainer instance.

> [TODO: Add screenshot of a configured config.yml file]

---

## 🔬 Step 4: Verify the Setup

After saving your configuration files, return to the terminal where `setup.sh` is paused and press **[Enter]**.

The script will automatically proceed to the final step: testing the webhook.

```
[6/6] Testing webhook connection...
This will run 'python main.py --test' to send a test message.
...
Test alert sent. Please check your Google Chat room.
```

- **Check your Google Chat room.** You should see a "Webhook Test Successful!" message.
- **If it fails,** the most likely cause is an incorrect URL in your `.env` file. Double-check for any copy-paste errors.

### Optional: Deeper Verification
You can test the individual monitor modules without sending real alerts by using the test scripts.

```bash
# Activate the environment
source .venv/bin/activate

# Test the Docker monitor logic
python test_docker.py

# Test the SSL monitor logic
python test_ssl.py

# Deactivate when done
deactivate
```

---

##  automating-the-checks" >⚙️ Step 5: Set Up Automation (Cron)

The final step is to schedule the monitor to run automatically.

1.  Open your user's crontab editor:
    ```bash
    crontab -e
    ```
2.  Paste in the schedule you want to use. It is recommended to use the full path to the `run_checks.sh` script for reliability.

**Recommended Schedule:**
```cron
# -----------------------------------------------------------------------------
# PinoySeoul Monitor Schedule
# -----------------------------------------------------------------------------
# Check Docker container health every 5 minutes.
*/5 * * * * /bin/bash /home/pinoyseoul/pinoyseoul-monitor/scripts/run_checks.sh docker >> /home/pinoyseoul/pinoyseoul-monitor/logs/cron.log 2>&1

# Check SSL certificates once a day at 8:00 AM.
0 8 * * * /bin/bash /home/pinoyseoul/pinoyseoul-monitor/scripts/run_checks.sh ssl >> /home/pinoyseoul/pinoyseoul-monitor/logs/cron.log 2>&1

# Check backup status once a day at 8:05 AM.
5 8 * * * /bin/bash /home/pinoyseoul/pinoyseoul-monitor/scripts/run_checks.sh backup >> /home/pinoyseoul/pinoyseoul-monitor/logs/cron.log 2>&1

# Send the daily summary report every day at 9:00 AM.
0 9 * * * /usr/bin/python3 /home/pinoyseoul/pinoyseoul-monitor/main.py --summary >> /home/pinoyseoul/pinoyseoul-monitor/logs/cron.log 2>&1
```

3.  Save and close the editor.

**Your monitoring system is now fully installed, configured, and automated!** 🚀
