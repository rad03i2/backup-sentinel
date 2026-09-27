# Backup Sentinel — English Guide

Backup Sentinel is a local Python command-line utility for creating timestamped directory snapshots, verifying them with SHA-256, listing stored snapshots, and restoring verified data behind overwrite guardrails.

> Current release: **1.0.0** · Python **3.10+** · License **MIT**

## Why it exists

Backup tools are most useful when their behavior is predictable. Backup Sentinel keeps the model deliberately small:

- each backup is a new self-contained snapshot;
- files are hashed before copy and verified after copy;
- a stored snapshot can be verified again later;
- a corrupted snapshot is refused during restore;
- existing destination files are protected by default;
- all operations remain local.

## Installation

```bash
git clone https://github.com/rad03i2/backup-sentinel.git
cd backup-sentinel
python -m pip install .
```

For development:

```bash
python -m pip install -e ".[dev]"
```

## Commands

### Create

```bash
backup-sentinel create ./important ./my-backups
```

Hidden files are excluded by default. Include them explicitly when needed:

```bash
backup-sentinel create ./important ./my-backups --include-hidden
```

### List

```bash
backup-sentinel list ./my-backups
```

The command emits JSON manifests so a `snapshot_id` can be copied into verify or restore commands.

### Verify

```bash
backup-sentinel verify ./my-backups 20260920T100000.000000Z
```

The result reports `ok`, `missing`, and `changed`. The CLI returns status 1 when verification fails.

### Restore

```bash
backup-sentinel restore ./my-backups 20260920T100000.000000Z ./restored
```

If destination files already exist, restore is refused unless overwrite is explicit:

```bash
backup-sentinel restore ./my-backups 20260920T100000.000000Z ./restored --overwrite
```

## Python API

```python
from pathlib import Path
from backup_sentinel import create_snapshot, verify_snapshot

manifest = create_snapshot(Path("important"), Path("backups"))
status = verify_snapshot(Path("backups"), manifest["snapshot_id"])

assert status["ok"]
```

The public package exports:

- `BackupError`
- `create_snapshot`
- `list_snapshots`
- `restore_snapshot`
- `sha256_file`
- `verify_snapshot`

## Snapshot layout

```text
my-backups/
└── snapshots/
    └── <snapshot-id>/
        ├── manifest.json
        └── data/
            └── ... original relative paths ...
```

The manifest format is currently version 1. It records relative path, byte size, and SHA-256 for each file plus snapshot metadata.

## Safety behavior

Backup Sentinel currently enforces these rules:

1. Source and backup repository cannot be the same directory or contain one another.
2. Symbolic links are not followed.
3. A copied backup file must match the SHA-256 calculated during the source scan.
4. Snapshot metadata is written atomically.
5. Restore begins only after the whole snapshot passes verification.
6. Existing destination files cause a conflict unless overwrite was explicitly requested.
7. Each restored file is verified before atomic promotion into its final path.

## Privacy and security

The tool performs no network access and needs no account, token, telemetry endpoint, or `.env` file.

Backup contents are **not encrypted**. SHA-256 verifies data against the stored manifest but does not authenticate the manifest itself. Protect backup media using operating-system permissions and, when appropriate, disk or volume encryption.

See [SECURITY.md](SECURITY.md) for the full trust boundary.

## Testing

```bash
ruff check .
pytest
```

CI runs those checks on Ubuntu, Windows, and macOS with Python 3.10, 3.12, and 3.13.

## Limitations

The current implementation uses full snapshots. It does not provide incremental backup, deduplication, compression, encryption, remote/cloud transport, scheduling, retention pruning, or a GUI.

Files that change while a snapshot is being created can cause verification to fail; retry after writes stop.

Metadata preservation is limited to the behavior of `shutil.copy2` and the host filesystem.

## More documentation

- [Main project page](README.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Security](SECURITY.md)
- [Roadmap](ROADMAP.md)
- [Contributing](CONTRIBUTING.md)
- [Brand system](docs/BRAND.md)

---

**Developer:** Radwan Abd alhady Ahmed · [@rad03i2](https://github.com/rad03i2)
