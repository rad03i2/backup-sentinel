"""Backup Sentinel: safe, local, verified directory snapshots."""

from .core import BackupError, create_snapshot, list_snapshots, restore_snapshot, sha256_file, verify_snapshot

__all__ = ["BackupError", "create_snapshot", "list_snapshots", "restore_snapshot", "sha256_file", "verify_snapshot"]
__version__ = "1.0.0"
