from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


class BackupError(RuntimeError):
    """Raised when a backup operation cannot be completed safely."""


@dataclass(frozen=True)
class FileRecord:
    path: str
    size: int
    sha256: str


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _inside(child: Path, parent: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def _validate(source: Path, repository: Path) -> tuple[Path, Path]:
    source, repository = source.resolve(), repository.resolve()
    if not source.is_dir():
        raise BackupError(f"Source is not a directory: {source}")
    if source == repository or _inside(repository, source) or _inside(source, repository):
        raise BackupError("Source and backup repository must not overlap")
    return source, repository


def scan(source: Path, include_hidden: bool = False) -> list[FileRecord]:
    source = source.resolve()
    records: list[FileRecord] = []
    for root, dirs, files in os.walk(source, followlinks=False):
        root_path = Path(root)
        dirs[:] = sorted(
            d for d in dirs
            if not (root_path / d).is_symlink() and (include_hidden or not d.startswith("."))
        )
        for name in sorted(files):
            path = root_path / name
            if path.is_symlink() or (not include_hidden and name.startswith(".")):
                continue
            try:
                stat = path.stat()
                records.append(FileRecord(path.relative_to(source).as_posix(), stat.st_size, sha256_file(path)))
            except (OSError, PermissionError) as exc:
                raise BackupError(f"Cannot read {path}: {exc}") from exc
    return records


def _atomic_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=".backup-sentinel-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(data, stream, ensure_ascii=False, indent=2, sort_keys=True)
            stream.write("\n")
        os.replace(temp_name, path)
    except Exception:
        Path(temp_name).unlink(missing_ok=True)
        raise


def create_snapshot(source: Path, repository: Path, *, include_hidden: bool = False) -> dict:
    source, repository = _validate(source, repository)
    repository.mkdir(parents=True, exist_ok=True)
    records = scan(source, include_hidden)
    snapshot_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    snapshot = repository / "snapshots" / snapshot_id
    data_dir = snapshot / "data"
    data_dir.mkdir(parents=True)
    try:
        for record in records:
            src = source / record.path
            dst = data_dir / record.path
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            if sha256_file(dst) != record.sha256:
                raise BackupError(f"Verification failed while copying {record.path}")
        manifest = {
            "format": 1,
            "snapshot_id": snapshot_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "source": str(source),
            "file_count": len(records),
            "total_bytes": sum(r.size for r in records),
            "files": [asdict(r) for r in records],
        }
        _atomic_json(snapshot / "manifest.json", manifest)
        return manifest
    except Exception:
        shutil.rmtree(snapshot, ignore_errors=True)
        raise


def list_snapshots(repository: Path) -> list[dict]:
    root = repository.resolve() / "snapshots"
    if not root.exists():
        return []
    result = []
    for manifest_path in sorted(root.glob("*/manifest.json"), reverse=True):
        try:
            result.append(json.loads(manifest_path.read_text(encoding="utf-8")))
        except (OSError, json.JSONDecodeError) as exc:
            raise BackupError(f"Invalid manifest: {manifest_path}: {exc}") from exc
    return result


def _load_snapshot(repository: Path, snapshot_id: str) -> tuple[Path, dict]:
    snapshot = repository.resolve() / "snapshots" / snapshot_id
    manifest_path = snapshot / "manifest.json"
    if not manifest_path.is_file():
        raise BackupError(f"Snapshot not found: {snapshot_id}")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise BackupError(f"Invalid snapshot manifest: {exc}") from exc
    if manifest.get("format") != 1 or not isinstance(manifest.get("files"), list):
        raise BackupError("Unsupported or malformed snapshot manifest")
    return snapshot, manifest


def verify_snapshot(repository: Path, snapshot_id: str) -> dict:
    snapshot, manifest = _load_snapshot(repository, snapshot_id)
    missing, changed = [], []
    for item in manifest["files"]:
        path = snapshot / "data" / item["path"]
        if not path.is_file():
            missing.append(item["path"])
        elif path.stat().st_size != item["size"] or sha256_file(path) != item["sha256"]:
            changed.append(item["path"])
    return {"snapshot_id": snapshot_id, "ok": not missing and not changed, "missing": missing, "changed": changed}


def restore_snapshot(repository: Path, snapshot_id: str, destination: Path, *, overwrite: bool = False) -> dict:
    snapshot, manifest = _load_snapshot(repository, snapshot_id)
    verification = verify_snapshot(repository, snapshot_id)
    if not verification["ok"]:
        raise BackupError("Refusing to restore a snapshot that fails verification")
    destination = destination.resolve()
    if _inside(destination, repository.resolve()) or destination == repository.resolve():
        raise BackupError("Restore destination must be outside the backup repository")
    conflicts = [item["path"] for item in manifest["files"] if (destination / item["path"]).exists()]
    if conflicts and not overwrite:
        raise BackupError(f"Restore would overwrite {len(conflicts)} existing file(s); use --overwrite")
    restored = 0
    for item in manifest["files"]:
        src = snapshot / "data" / item["path"]
        dst = destination / item["path"]
        dst.parent.mkdir(parents=True, exist_ok=True)
        fd, temp_name = tempfile.mkstemp(prefix=".restore-", dir=dst.parent)
        os.close(fd)
        temp = Path(temp_name)
        try:
            shutil.copy2(src, temp)
            if sha256_file(temp) != item["sha256"]:
                raise BackupError(f"Restore verification failed: {item['path']}")
            os.replace(temp, dst)
            restored += 1
        finally:
            temp.unlink(missing_ok=True)
    return {"snapshot_id": snapshot_id, "destination": str(destination), "restored": restored}
