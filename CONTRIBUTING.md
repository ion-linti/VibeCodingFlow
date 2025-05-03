
# Contributing to VibeCodingFlow

Thanks for taking the time to help improve **VibeCodingFlow**! Below is a quick guide to get you productive.

## Workflow

1. Fork the repository and create a feature branch.
2. Make your changes.
3. Ensure tests and linters pass:
   ```bash
   pip install -e .[dev]
   ruff .
   black --check .
   pytest
   ```
4. Commit using conventional commits (`feat:`, `fix:`, etc.).
5. Open a pull request against `main`.

## Style

* Python ≥3.10, **PEP 8** compliant.
* Auto‑format with **Black**, lint with **Ruff**.
* Type‑annotate all public functions.
* Keep docstrings short but useful (NumPy style).

## Tests

* Add unit tests in the `tests/` folder.
* Use *pytest*; async tests are supported via `pytest-asyncio`.

## Changelog

Add an entry to `CHANGELOG.md` under *Unreleased* if your change is user‑visible.

---

Happy coding! 🚀
