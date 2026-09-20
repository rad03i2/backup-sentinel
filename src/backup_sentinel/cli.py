from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .core import BackupError, create_snapshot, list_snapshots, restore_snapshot, verify_snapshot

VERSION = "1.0.0"


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="backup-sentinel", description="Safe local versioned backups")
    p.add_argument("--version", action="version", version=f"Backup Sentinel {VERSION} — Radwan Abdulhadi Ahmed / @rad03i2")
    sub = p.add_subparsers(dest="command", required=True)

    create = sub.add_parser("create", help="Create and verify a snapshot")
    create.add_argument("source", type=Path)
    create.add_argument("repository", type=Path)
    create.add_argument("--include-hidden", action="store_true")

    ls = sub.add_parser("list", help="List snapshots")
    ls.add_argument("repository", type=Path)

    verify = sub.add_parser("verify", help="Verify snapshot integrity")
    verify.add_argument("repository", type=Path)
    verify.add_argument("snapshot_id")

    restore = sub.add_parser("restore", help="Restore a verified snapshot")
    restore.add_argument("repository", type=Path)
    restore.add_argument("snapshot_id")
    restore.add_argument("destination", type=Path)
    restore.add_argument("--overwrite", action="store_true")
    return p


def _print(value: object) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2))


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command == "create":
            _print(create_snapshot(args.source, args.repository, include_hidden=args.include_hidden))
        elif args.command == "list":
            _print(list_snapshots(args.repository))
        elif args.command == "verify":
            result = verify_snapshot(args.repository, args.snapshot_id)
            _print(result)
            return 0 if result["ok"] else 1
        elif args.command == "restore":
            _print(restore_snapshot(args.repository, args.snapshot_id, args.destination, overwrite=args.overwrite))
        return 0
    except BackupError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
