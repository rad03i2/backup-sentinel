import json
from pathlib import Path

import pytest

from backup_sentinel.core import BackupError, create_snapshot, list_snapshots, restore_snapshot, verify_snapshot


def make_source(tmp_path: Path) -> Path:
    source = tmp_path / "source"
    (source / "docs").mkdir(parents=True)
    (source / "docs" / "note.txt").write_text("hello", encoding="utf-8")
    (source / "data.bin").write_bytes(b"\x00\x01\x02")
    (source / ".secret").write_text("hidden", encoding="utf-8")
    return source


def test_create_verify_list_restore(tmp_path: Path) -> None:
    source = make_source(tmp_path)
    repo = tmp_path / "backups"
    manifest = create_snapshot(source, repo)
    assert manifest["file_count"] == 2
    assert not any(item["path"] == ".secret" for item in manifest["files"])
    assert verify_snapshot(repo, manifest["snapshot_id"])["ok"] is True
    assert list_snapshots(repo)[0]["snapshot_id"] == manifest["snapshot_id"]

    restored = tmp_path / "restored"
    result = restore_snapshot(repo, manifest["snapshot_id"], restored)
    assert result["restored"] == 2
    assert (restored / "docs" / "note.txt").read_text(encoding="utf-8") == "hello"
    assert (restored / "data.bin").read_bytes() == b"\x00\x01\x02"


def test_include_hidden(tmp_path: Path) -> None:
    source = make_source(tmp_path)
    manifest = create_snapshot(source, tmp_path / "repo", include_hidden=True)
    assert any(item["path"] == ".secret" for item in manifest["files"])


def test_tampering_is_detected_and_restore_refused(tmp_path: Path) -> None:
    source = make_source(tmp_path)
    repo = tmp_path / "repo"
    manifest = create_snapshot(source, repo)
    backed_up = repo / "snapshots" / manifest["snapshot_id"] / "data" / "docs" / "note.txt"
    backed_up.write_text("tampered", encoding="utf-8")
    result = verify_snapshot(repo, manifest["snapshot_id"])
    assert result["ok"] is False
    assert "docs/note.txt" in result["changed"]
    with pytest.raises(BackupError, match="fails verification"):
        restore_snapshot(repo, manifest["snapshot_id"], tmp_path / "restore")


def test_restore_conflict_requires_overwrite(tmp_path: Path) -> None:
    source = make_source(tmp_path)
    repo = tmp_path / "repo"
    manifest = create_snapshot(source, repo)
    destination = tmp_path / "destination"
    (destination / "docs").mkdir(parents=True)
    (destination / "docs" / "note.txt").write_text("keep me", encoding="utf-8")
    with pytest.raises(BackupError, match="overwrite"):
        restore_snapshot(repo, manifest["snapshot_id"], destination)
    restore_snapshot(repo, manifest["snapshot_id"], destination, overwrite=True)
    assert (destination / "docs" / "note.txt").read_text(encoding="utf-8") == "hello"


def test_overlapping_paths_rejected(tmp_path: Path) -> None:
    source = make_source(tmp_path)
    with pytest.raises(BackupError, match="overlap"):
        create_snapshot(source, source / "backup")


def test_manifest_is_valid_json(tmp_path: Path) -> None:
    source = make_source(tmp_path)
    repo = tmp_path / "repo"
    manifest = create_snapshot(source, repo)
    path = repo / "snapshots" / manifest["snapshot_id"] / "manifest.json"
    loaded = json.loads(path.read_text(encoding="utf-8"))
    assert loaded["format"] == 1
    assert loaded["total_bytes"] == 8
