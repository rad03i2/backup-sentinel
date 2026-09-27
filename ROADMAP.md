# Roadmap

Backup Sentinel intentionally keeps future work separate from current capabilities.

The following are **ideas, not implemented features or release promises**.

## Candidate direction

### Content-addressed deduplication

Explore storing repeated file content once while keeping each snapshot logically self-contained from the user's perspective.

Any design must preserve understandable verification and restore behavior.

### Explicit retention policies

Explore opt-in policies for deciding which snapshots may be pruned.

Retention must never introduce silent deletion. A future implementation should make policy evaluation visible and destructive actions explicit.

## Design constraints for future work

Future features should preserve the existing principles:

- local-first behavior by default;
- deterministic and inspectable snapshot metadata;
- no implicit overwrite;
- verification before restore;
- no hidden deletion;
- clear separation between data integrity and cryptographic authenticity.

Features such as cloud transport, scheduling, compression, encryption, and a GUI are **not part of the current release** and are not committed roadmap items here.
