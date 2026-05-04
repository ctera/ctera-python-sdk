# Contributing to ctera-python-sdk

Thank you for contributing to the CTERA Python SDK. This guide covers prerequisites, local development setup, branching, testing, and the release process.

## Prerequisites

- Python 3.10, 3.11, or 3.12
- [tox](https://tox.readthedocs.io/) (`pip install tox`)
- Git

## Local Development Setup

```bash
# Clone the repository
git clone https://github.com/ctera/ctera-python-sdk.git
cd ctera-python-sdk

# Install in editable mode with development dependencies
pip install -e .
pip install -r ut-requirements.txt

# Or run everything through tox (recommended)
pip install tox
tox            # runs lint + unit tests
tox -e ut      # unit tests only
tox -e lint    # lint only
tox -e docs    # build documentation
```

## Branching Model

| Branch | Purpose |
|--------|---------|
| `master` | Stable, released code. Protected — PRs only. |
| Feature branches | Named `<jira-ticket>-<short-description>` or `no-ticket-<short-description>` |
| Dependabot | Dependency bump branches managed automatically |

**Never commit directly to `master`.** All changes go through pull requests.

## Running Tests

```bash
# Full suite (lint + unit tests, as run in CI)
tox

# Unit tests only with verbose output
tox -e ut -- --verbose

# Single test module
tox -e ut -- tests/ut/core/admin/test_users.py

# Coverage report
tox -e ut
open reports/coverage/index.html
```

The CI gate requires **70% line coverage** (threshold will increase to 80% as part of the M3 roadmap milestone).

## Code Style

- Line length: 140 characters (configured in `.flake8`)
- Linting: `flake8` + `pylint` (run via `tox -e lint`)
- All public methods should have docstrings

## Pull Request Process

1. Create a branch from `master`:
   ```bash
   git checkout -b my-feature-branch origin/master
   ```
2. Make your changes and add/update tests.
3. Run `tox` locally and confirm it passes.
4. Push your branch and open a pull request against `master`.
5. The CI workflow (`.github/workflows/ci.yml`) runs automatically on every PR.
6. At least one CODEOWNER review is required before merging.
7. Squash-merge is preferred to keep the `master` history clean.

## Release Process

Releases are published to [PyPI](https://pypi.org/project/cterasdk/) automatically when a GitHub Release is created.

1. Ensure `master` is green.
2. Create a GitHub Release with a semver tag (e.g. `2.21.0`).
3. The `deploy` job in CI builds and publishes to PyPI automatically.
4. After publishing, verify the new version appears on PyPI and ReadTheDocs.

**Update the changelog** (`docs/source/UserGuides/Miscellaneous/Changelog.rst`) before tagging a release.

## Reporting Issues

Please open an issue at [github.com/ctera/ctera-python-sdk/issues](https://github.com/ctera/ctera-python-sdk/issues).
Include the SDK version (`pip show cterasdk`), Python version, and a minimal reproducible example.

## Maintainers

- [Saimon Michelson](https://github.com/saimonmichelson) — original author
- [Asa Fainshtein](https://github.com/asafa) — Portal Group lead (CTERA Networks)
