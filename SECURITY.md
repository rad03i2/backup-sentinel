# Security Policy

## Supported version
Security fixes target the latest release on the default branch.

## Security model
Backup Sentinel is local-only and does not transmit data. Snapshot contents are **not encrypted**. SHA-256 integrity checks detect accidental corruption or modification when the manifest remains trustworthy; they are not a MAC or digital signature. Protect the repository with filesystem permissions and, where appropriate, full-disk or volume encryption.

The tool does not follow symbolic links, refuses overlapping source/repository paths, verifies copied content, refuses corrupted snapshots during restore, and protects existing restore targets unless `--overwrite` is explicitly supplied.

## Reporting a vulnerability
Please use GitHub's private security reporting feature for this repository when available. Do not publish credentials, private files, or exploit data in a public issue.
