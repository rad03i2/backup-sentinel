# Security Policy

## Supported version

Security fixes target the latest code on the default branch and the latest tagged release when applicable.

## Security model

Backup Sentinel is a local-only utility. It does not upload files, contact a remote API, collect telemetry, or require secrets.

The core safety model is based on predictable local behavior:

- source and backup repository paths may not overlap;
- symbolic links are not followed;
- file contents are hashed with SHA-256;
- copied backup files are verified against the source scan;
- malformed or missing manifests are rejected;
- a snapshot must pass verification before restore;
- restore protects existing destination files unless overwrite is explicit;
- restored files are verified before atomic promotion into place.

## Important boundary: integrity is not authenticity

Snapshot data is **not encrypted**.

SHA-256 lets Backup Sentinel detect data that no longer matches the stored manifest. It does not authenticate the manifest itself. An attacker who can modify both the backup data and `manifest.json` can replace both consistently.

Use filesystem permissions and, where appropriate, full-disk or volume encryption to protect the backup repository.

## Data exposure

The manifest stores the original absolute source path and the relative path, size, and SHA-256 digest of every backed-up file. Treat manifests as potentially sensitive metadata.

Do not publish real manifests when they reveal private directory names or filenames.

## Reporting a vulnerability

Prefer GitHub private security reporting for this repository when it is available.

Please include:

- affected version or commit;
- operating system and Python version;
- a concise reproduction;
- expected behavior;
- observed behavior;
- impact assessment;
- sanitized logs or sample data when useful.

Do not include credentials, private backup contents, personal documents, or secrets in public issues.

## Out of scope

The project does not currently claim to provide encryption, authenticated manifests, ransomware resistance, remote replication, immutable storage, or secure deletion.
