# Contributing to Backup Sentinel

Thanks for helping improve Backup Sentinel. Contributions should preserve the project's conservative backup and restore behavior.

## Development setup

Use Python 3.10 or newer.

```bash
git clone https://github.com/rad03i2/backup-sentinel.git
cd backup-sentinel
python -m pip install -e ".[dev]"
```

## Before changing behavior

Backup and restore software should fail safely. Changes must not introduce:

- silent deletion;
- implicit overwrite;
- hidden network upload;
- secret collection;
- automatic trust of unverified snapshot data;
- symlink traversal that changes the current safety boundary.

If a proposal intentionally changes one of those boundaries, explain the security impact clearly in the pull request.

## Quality checks

Run:

```bash
ruff check .
pytest
```

Behavior changes should include focused tests. Documentation must describe only implemented behavior and should keep roadmap ideas clearly labeled as future work.

## Pull requests

Prefer small, reviewable pull requests with:

1. a clear problem statement;
2. the smallest reasonable implementation;
3. tests for behavioral changes;
4. documentation updates when user-facing behavior changes;
5. no unrelated formatting churn.

The pull request template in `.github/PULL_REQUEST_TEMPLATE.md` provides a concise checklist.

## Bug reports

Useful bug reports include:

- operating system;
- Python version;
- Backup Sentinel version or commit;
- exact command used;
- expected result;
- actual result;
- sanitized error output;
- whether symlinks, hidden files, or existing restore targets were involved.

Never attach private backup data or secrets.

## Style

- Keep the code straightforward and auditable.
- Prefer standard-library solutions when they remain clear.
- Keep public behavior compatible unless a change is justified and documented.
- Preserve JSON output semantics for automation users when possible.

## Maintainer

**رضوان عبدالهادي**  
**Radwan Abd alhady Ahmed** · [@rad03i2](https://github.com/rad03i2)
