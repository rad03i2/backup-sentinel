# Changelog

All notable project changes are documented here.

## Unreleased

### Repository presentation

- Added a dedicated Backup Sentinel visual identity.
- Added canonical project cover and square logo assets.
- Reorganized the main README around the backup lifecycle, safety model, and current boundaries.
- Added separate English and Arabic guides.
- Added architecture and brand documentation.
- Added contribution, security, roadmap, and GitHub collaboration guidance.

No backup engine or CLI behavior was changed by this documentation and identity refresh.

## 1.0.0

Initial public release.

### Included

- Timestamped full directory snapshots.
- SHA-256 source scanning and post-copy verification.
- Snapshot manifests in JSON format.
- Snapshot listing.
- Later integrity verification.
- Guarded restore.
- Existing-file overwrite protection.
- Hidden-file opt-in.
- Symlink exclusion.
- Source/repository overlap protection.
- Python API and JSON CLI output.
- Ruff and Pytest CI across Linux, Windows, and macOS.
