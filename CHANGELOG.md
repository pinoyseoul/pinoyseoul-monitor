# Changelog

## 2025-11-10

### Fixed
- Resolved scheduling issues for daily and listener summary reports.
  - Implemented `--scheduled-listener-summary` argument in `main.py` to ensure AzuraCast listener summaries are sent only at their configured time and timezone.
  - Updated cron jobs for both daily summary and AzuraCast listener summary to utilize their respective scheduled arguments (`--scheduled-summary` and `--scheduled-listener-summary`), ensuring adherence to `config.yml`'s time and timezone settings.

## 2025-11-09

### Fixed
- Corrected daily summary report timing by implementing timezone awareness. The application now uses the configured timezone (e.g., Asia/Manila) to send scheduled reports at the correct local time, resolving an issue where reports were sent at incorrect times due to server UTC settings.

### Added
- New `general.timezone` setting in `config.yml` to specify the local timezone.
- New `--scheduled-summary` command-line argument for `main.py` to trigger daily summaries only at the configured time in the specified timezone.
- Added `pytz` to `requirements.txt` for timezone handling.

### Changed
- Updated cron job examples in `README.md` and `scripts/run_checks.sh` to use the new `--scheduled-summary` argument for daily summaries.