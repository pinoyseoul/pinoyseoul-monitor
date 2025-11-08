# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
