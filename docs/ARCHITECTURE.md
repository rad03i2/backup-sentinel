# Architecture

Backup Sentinel is intentionally small. Its design favors auditable file operations over abstraction-heavy infrastructure.

## Components

```text
CLI (src/backup_sentinel/cli.py)
        │
        ▼
Public operations
create_snapshot
list_snapshots
verify_snapshot
restore_snapshot
        │
        ▼
Filesystem + SHA-256
        │
        ▼
<repository>/snapshots/<snapshot-id>/
├── manifest.json
└── data/
```

### `cli.py`

The command-line layer parses four commands:

- `create`
- `list`
- `verify`
- `restore`

Results are emitted as JSON. Domain failures are surfaced through `BackupError` and return a non-zero CLI status.

### `core.py`

The core module owns scanning, hashing, snapshot creation, manifest persistence, verification, and restore behavior.

Important implementation choices:

- SHA-256 is calculated for source files during scanning.
- Each copied backup file is hashed again after `shutil.copy2`.
- Snapshot metadata is written atomically through a temporary file and `os.replace`.
- Restore first verifies the full snapshot.
- Restored files are copied to a temporary file, verified, then promoted with `os.replace`.
- Existing destination files are protected unless overwrite is explicitly requested.
- Symbolic links are not followed.
- Source and backup repository paths are forbidden from overlapping.

## Snapshot format

Each snapshot is self-contained:

```text
my-backups/
└── snapshots/
    └── 20260920T100000.000000Z/
        ├── manifest.json
        └── data/
            └── ... original relative paths ...
```

The manifest format is currently version `1`. Each file record stores:

- relative path;
- byte size;
- SHA-256 digest.

The manifest also records snapshot creation time, source path, file count, and total bytes.

## Safety invariants

The implementation is built around a small set of invariants:

| Invariant | Enforcement |
|---|---|
| Backup source and repository do not overlap | Path validation before snapshot creation |
| Symlinks are not traversed | `os.walk(..., followlinks=False)` plus explicit symlink filtering |
| Copied backup data matches scanned source data | Post-copy SHA-256 comparison |
| Corrupted snapshots are not restored | Full verification before restore |
| Existing destination files are not silently replaced | Conflict check unless `--overwrite` is used |
| Restore writes are promoted atomically per file | Temporary copy + hash check + `os.replace` |

## Trust boundary

Backup Sentinel detects corruption or modification by comparing data against the stored SHA-256 values. It does **not** cryptographically authenticate the manifest itself.

An attacker who can modify both backup data and `manifest.json` can replace both consistently. Backup storage should therefore be protected with appropriate filesystem permissions and, where required, disk or volume encryption.

The tool itself does not implement encryption, cloud transport, scheduling, compression, deduplication, or retention pruning.

## Tests

`tests/test_backup.py` exercises the main safety behavior:

- create → verify → list → restore;
- hidden-file handling;
- tamper detection;
- refusal to restore corrupted data;
- overwrite protection;
- overlap rejection;
- JSON manifest validity.

CI runs Ruff and Pytest across Ubuntu, Windows, and macOS on Python 3.10, 3.12, and 3.13.
