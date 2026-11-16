# Contributing

Thank you for considering a contribution to ParkSmart Kenya.

The project is an early-stage educational prototype. Contributions should improve correctness, clarity, security, accessibility, or documented functionality without claiming unverified production readiness.

## Before starting

1. Read the [README](README.md) and [SECURITY](SECURITY.md) policy.
2. Search existing issues and pull requests to avoid duplicate work.
3. For substantial changes, open an issue first to discuss the problem and approach.
4. Do not submit secrets, real personal data, payment credentials, or client-owned code.

## Development setup

Use Python 3.10 or newer:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\Activate.ps1
python -m pip install -e ".[dev]"
python -m pytest -q
```

## Pull requests

- Keep changes focused and explain the problem they solve.
- Add or update tests for changed behaviour.
- Update documentation when commands, configuration, or behaviour changes.
- Do not add real payment processing or physical barrier-control claims without a separately reviewed design.
- Describe limitations and security implications honestly.
- Ensure the GitHub Actions test workflow passes.

By submitting a contribution, you agree that it may be distributed under the repository's MIT licence.
