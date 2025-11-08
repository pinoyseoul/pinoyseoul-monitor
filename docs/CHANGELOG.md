# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- **Motivational Quotes:** The daily morning and evening summary reports now include a randomly selected, Korean-themed motivational quote to enhance team morale.
  - A new `utils/quotes.py` module was created to store and manage 100 morning and 100 evening quotes.

### Fixed
- **Backup Monitor Compatibility:** The backup check (`monitors/backup_check.py`) was updated to use the `rclone lsjson` command, ensuring compatibility with older versions of rclone that do not support formatted output. This resolves a critical bug that prevented the backup check from running correctly.
- **Configuration Clarity:** Removed duplicated `azuracast` sections from `config.example.yml` to prevent confusion and ensure a single source of truth for the configuration.

### Changed
- **AzuraCast Daily Summary Time:** Updated the `daily_summary_time` in `config.example.yml` for the AzuraCast listener report from 8 PM (20:00) to 9 PM (21:00) to align with other daily summary schedules.

---

## [1.1.0] - 2025-11-08

### Added
- **AzuraCast Daily Listener Summary:** Added `monitors/azuracast_check.py` to connect to the AzuraCast API and send a daily report of the total unique listeners for the day.
- Added a new `--listener-summary` command to `main.py` to trigger the report.
- Added a new `azuracast` section to `config.yml` and `AZURACAST_API_KEY` to `.env`.

### Changed
- Updated `utils/google_chat.py` with a new `send_azuracast_summary` function for the listener report.

---

## [1.0.0] - 2025-11-08

### Added
- **Initial Release:** First stable version of the PinoySeoul Monitoring Service.
- **Docker Monitoring:** Added `monitors/docker_health.py` to check the status of all running and stopped containers, with alerting for stopped containers and restart loops.
- **SSL Certificate Monitoring:** Added `monitors/ssl_check.py` to verify SSL certificates for a configurable list of domains, with critical/warning alerts for expiry thresholds.
- **Backup Verification:** Added `monitors/backup_check.py` to parse `rclone` log files, verifying backup completion, size, and error status.
- **Google Chat Integration:** Created `utils/google_chat.py` to send beautifully formatted Card v2 alerts and daily summaries to a configured webhook.
- **Centralized Configuration:** Implemented a comprehensive `config.yml` to manage all application settings, with secrets loaded from a `.env` file.
- **Advanced Logging:** Created `utils/logger.py` to provide application-wide logging to both the console and a rotating daily log file.
- **CLI Entrypoint:** Built `main.py` with `argparse` to allow running specific checks (`--check`), sending summaries (`--summary`), and testing (`--test`).
- **Automation Scripts:**
  - `scripts/setup.sh`: A guided, automated installer for easy deployment.
  - `scripts/run_checks.sh`: A robust cron wrapper to reliably execute checks.
- **Documentation:**
  - Created `README.md` with a full project overview.
  - Created `SETUP_GUIDE.md` for detailed installation instructions.
  - Created `ARCHITECTURE.md` with technical diagrams and data flows.
  - Created this `CHANGELOG.md`.
