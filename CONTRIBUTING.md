# Contributing

Thanks for helping improve Backup Sentinel.

1. Fork the repository and create a focused branch.
2. Use Python 3.10+ and install `python -m pip install -e ".[dev]"`.
3. Keep backup operations conservative: never introduce silent deletion, implicit overwrite, secret collection, or network upload.
4. Add or update tests for behavioral changes.
5. Run `ruff check .` and `pytest` before opening a pull request.
6. Keep documentation aligned with implemented behavior.

Small, reviewable pull requests are preferred. Bug reports should include the operating system, Python version, command used, expected behavior, and sanitized error output.

Maintainer / Author: Radwan Abdulhadi Ahmed (رضوان عبدالهادي أحمد), GitHub @rad03i2.
