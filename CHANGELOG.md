# Changelog

## 2025-11-11

### Added
- **Auto-Remediation (Self-Healing):** The Docker monitor now automatically restarts any service it finds in a "stopped" state and sends an informational alert upon success.
- **Stateful "Resolved" Alerts:** The monitoring system now remembers when a service is down and sends a follow-up "ALL CLEAR" message when the issue has been resolved.
- Created a new `utils/state_manager.py` utility to handle state persistence in a `monitor_state.json` file.

### Fixed
- **Backup System:** Repaired the entire backup process by fixing a `tar` syntax error in `backup.sh`, moving the cron job to the system-wide crontab to run as `root`, and correcting the file permissions on `rclone.conf`.
- **Timezone Synchronization:** Corrected all cron jobs (for both the monitor and other system scripts) to run on the `Asia/Manila` timezone, fixing the root cause of delayed or missed notifications.
- **Silent Failures:** Fixed multiple logical flaws that were preventing alerts from being sent for stale backups and `rclone` command failures.

### Improved
- **User-Friendly Alerts:** All alert messages have been completely rewritten to be non-technical, focusing on business impact and providing a clear call to action (contacting `tech@pinoyseoul.com`).
- **Documentation:** Comprehensively updated `README.md` with all new features and corrected configurations.

## 2025-11-10

### Fixed
- **Cron Job Reliability:** Fixed an issue where scheduled summary reports (9 AM daily, 9 PM listener) were failing silently. Replaced direct Python calls in the crontab with a new robust wrapper script (`scripts/run_summary.sh`) that ensures the virtual environment is properly activated, mirroring the reliability of the check-based cron jobs.
- Resolved scheduling issues for daily and listener summary reports.
  - Implemented `--scheduled-listener-summary` argument in `main.py` to ensure AzuraCast listener summaries are sent only at their configured time and timezone.
  - Updated cron jobs for both daily summary and AzuraCast listener summary to utilize their respective scheduled arguments (`--scheduled-summary` and `--scheduled-listener-summary`), ensuring adherence to `config.yml`'s time and timezone settings.

### Changed
- **AzuraCast Listener Logic:** Improved the reliability of the AzuraCast listener count. The script no longer assumes the "unique listeners" metric is the first in the API response. It now actively searches for the correct metric by name, preventing it from pulling the wrong data if the API's structure changes.

## 2025-11-09

### Fixed
- Corrected daily summary report timing by implementing timezone awareness. The application now uses the configured timezone (e.g., Asia/Manila) to send scheduled reports at the correct local time, resolving an issue where reports were sent at incorrect times due to server UTC settings.

### Added
- New `general.timezone` setting in `config.yml` to specify the local timezone.
- New `--scheduled-summary` command-line argument for `main.py` to trigger daily summaries only at the configured time in the specified timezone.
- Added `pytz` to `requirements.txt` for timezone handling.

### Changed
- Updated cron job examples in `README.md` and `scripts/run_checks.sh` to use the new `--scheduled-summary` argument for daily summaries.