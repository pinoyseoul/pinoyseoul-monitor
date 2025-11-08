# PinoySeoul Monitor: Deployment Checklist

This document provides a comprehensive checklist for deploying the PinoySeoul Monitoring Service to a production server. Follow these steps to ensure a smooth and successful deployment.

---

## ✅ 1. Pre-Deployment

Perform these checks on your local machine and server before uploading any files.

- [ ] **Backup Server:** Before making any changes, take a snapshot or backup of your server via your cloud provider's dashboard. This is your safety net.

- [ ] **Verify Python Version:** SSH into your server and confirm that Python 3.8+ is installed.
  ```bash
  python3 --version
  ```

- [ ] **Verify Docker Access:** Ensure the Docker daemon is running and your user has permission to access it. The `docker ps` command should execute without a "permission denied" error. If it fails, you may need to run `sudo usermod -aG docker $USER` and then log out and back in.
  ```bash
  docker ps
  ```

- [ ] **Test SSH Connection:** Confirm you have reliable, key-based SSH access to the server.

---

## 📤 2. Upload Code

Choose one of the following methods to get the project code onto your server.

### Option A: Using `git clone` (Recommended)
This is the best method if your project is in a GitHub repository.

```bash
# On your server
git clone <your-repository-url> pinoyseoul-monitor
cd pinoyseoul-monitor
```

### Option B: Using `scp`
Use this method to copy the files from your local machine if you are not using Git.

```bash
# On your local machine
scp -r /path/to/your/local/pinoyseoul-monitor/ your_user@your_server_ip:~/
```

---

## 🖥️ 3. Server Setup

Now, run the automated setup script and configure the monitor for this specific server.

- [ ] **Run `setup.sh`:** This script will prepare the environment. It will pause and wait for you to configure the files.
  ```bash
  # From within the pinoyseoul-monitor directory on your server
  bash scripts/setup.sh
  ```

- [ ] **Edit `config.yml`:** While the script is paused, open the configuration file and verify all paths and settings are correct for the server environment.
  ```bash
  nano config.yml
  ```

- [ ] **Add Webhook URL:** Open the `.env` file and paste in your production Google Chat webhook URL.
  ```bash
  nano .env
  ```

- [ ] **Test Webhook from Server:** After saving your configuration, press **[Enter]** in the terminal where `setup.sh` is running. It will automatically run a test to confirm the server can reach the Google Chat webhook. Verify you receive the test message.

---

## 🔬 4. Test on Server

Before automating, run each monitor manually to ensure it works correctly in the server environment.

- [ ] **Activate Virtual Environment:**
  ```bash
  source .venv/bin/activate
  ```

- [ ] **Test Docker Monitor:** Run the Docker test script. Verify that the `total_containers` count matches your `docker ps` output.
  ```bash
  python test_docker.py
  ```

- [ ] **Test SSL Monitor:** Run the SSL test script. Verify that it correctly shows your domain as "VALID".
  ```bash
  python test_ssl.py
  ```

- [ ] **Test Backup Monitor:** Run the backup test script. This will parse your *sample* log file.
  ```bash
  python test_backup.py
  ```

- [ ] **Final Check:** Manually run a real check to ensure everything works together.
  ```bash
  # This will send a real alert if issues are found
  python main.py --check all
  ```

---

## 🤖 5. Setup Cron Jobs (Automation)

Once all tests pass, schedule the monitor to run automatically using `cron`.

- [ ] **Open Crontab Editor:**
  ```bash
  crontab -e
  ```

- [ ] **Add a Test Job:** To verify `cron` is working correctly, first add a temporary job that runs every minute.
  ```cron
  # Test job - runs every minute
  * * * * * /bin/bash /home/pinoyseoul/pinoyseoul-monitor/scripts/run_checks.sh docker >> /home/pinoyseoul/pinoyseoul-monitor/logs/cron_test.log 2>&1
  ```

- [ ] **Verify Cron is Running:** Wait a minute or two, then check the log file. If you see output, cron is working.
  ```bash
  tail -f /home/pinoyseoul/pinoyseoul-monitor/logs/cron_test.log
  ```
  Once verified, remove the test line from your crontab.

---

## 🧐 6. Monitor for 24 Hours

- [ ] **Observe Alerts:** For the first 24 hours, keep a close eye on the Google Chat room.
- [ ] **Check for False Positives:** Are you getting alerts that aren't real issues? You may need to adjust thresholds in `config.yml` (e.g., `min_size_mb` for backups).
- [ ] **Check for Missed Alerts:** Intentionally stop a non-critical container for a few minutes. Did you receive a `CRITICAL` alert as expected?
- [ ] **Take Screenshots:** Now is the perfect time to take screenshots of the real alerts and daily summaries for your portfolio!
  > [TODO: Add screenshot of a real critical alert from the server]
  >
  > [TODO: Add screenshot of a real daily summary from the server]

---

## ✅ 7. Post-Deployment

- [ ] **Set Final Cron Schedule:** Open your crontab (`crontab -e`) one last time and replace the test job with your final, desired schedule.
  ```cron
  # Final schedule
  */5 * * * * /bin/bash /home/pinoyseoul/pinoyseoul-monitor/scripts/run_checks.sh docker >> /home/pinoyseoul/pinoyseoul-monitor/logs/cron.log 2>&1
  0 8 * * * /bin/bash /home/pinoyseoul/pinoyseoul-monitor/scripts/run_checks.sh ssl >> /home/pinoyseoul/pinoyseoul-monitor/logs/cron.log 2>&1
  5 8 * * * /bin/bash /home/pinoyseoul/pinoyseoul-monitor/scripts/run_checks.sh backup >> /home/pinoyseoul/pinoyseoul-monitor/logs/cron.log 2>&1
  0 9 * * * /usr/bin/python3 /home/pinoyseoul/pinoyseoul-monitor/main.py --summary >> /home/pinoyseoul/pinoyseoul-monitor/logs/cron.log 2>&1
  ```

- [ ] **Document Issues:** Add any unexpected issues or solutions you discovered during deployment to a personal notes file or update the project's documentation.

- [ ] **Update README:** If you made any significant changes, update the main `README.md` to reflect them.

**Deployment complete!** 🎉
