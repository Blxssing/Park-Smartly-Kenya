# ParkSmart Kenya

ParkSmart Kenya is an early-stage, open-source Python parking-management prototype. It demonstrates vehicle entry and exit, parking-slot allocation, sample fee calculation, simulated payment-state handling, and FIFO waiting-queue promotion using SQLite.

> **Status and limitations:** This is a learning and development prototype, not production-ready parking, payment, access-control, or security software. Payments and barrier actions are simulated. Do not expose the demo server to the public internet or use it with real customer/payment data or physical barriers.

## Features

- Display available and occupied slots.
- Register vehicle entry and assign the first available slot.
- Reject duplicate active or queued registrations.
- Queue vehicles in FIFO order when full.
- Calculate parking duration and apply a sample KSh tariff.
- Keep slots occupied until a simulated payment is recorded.
- Promote the next waiting vehicle after payment.
- Persist slots, sessions, payments and waiting queue in SQLite.
- Demonstrate linked-node stack (LIFO) and queue (FIFO) structures.
- Run tests with pytest.

## Sample tariff

| Duration | Fee |
| --- | ---: |
| Up to 30 minutes | KSh 0 |
| 31 minutes to 2 hours | KSh 50 |
| 121 minutes to 4 hours | KSh 100 |
| 241 minutes to 6 hours | KSh 300 |
| More than 6 hours | KSh 500 |

This is example logic, not a recommendation or representation of any operator's actual prices.

## Requirements

- Python 3.10+
- pip

No third-party runtime dependencies are required. pytest is used for development.

## Setup

```bash
git clone https://github.com/Blxssing/Park-Smartly-Kenya.git
cd Park-Smartly-Kenya
python -m venv .venv
```

Activate the environment:

```bash
# macOS / Linux
source .venv/bin/activate
# Windows PowerShell
.venv\\Scripts\\Activate.ps1
```

Install the package and development dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

## Run tests

```bash
python -m pytest -q
```

## Run the local web demonstration

```bash
python -m app.web
```

Open http://127.0.0.1:8000. The app creates `parksmart_web.db` in the current directory. Set `PARKSMART_DB_PATH` to choose another database file.

The built-in HTTP server is intentionally minimal. It has no authentication, real payment integration, TLS setup, or production deployment hardening.

## Project structure

```text
app/                 Application modules
  database.py        SQLite persistence and schema
  datastructures.py  Linked-node stack and queue
  parking.py         Parking business rules
  web.py             Minimal local web demo
  security.py        HTML output escaping helper
docs/                Algorithm and data-structure notes
tests/               Automated tests
.github/workflows/   Continuous integration
CONTRIBUTING.md      Contribution guidelines
SECURITY.md          Security reporting policy
LICENSE              MIT License
pyproject.toml       Package and tool configuration
schema.sql           Standalone database schema
```

## Contributing

Contributions are welcome. Read [CONTRIBUTING.md](CONTRIBUTING.md), open an issue before substantial changes, and include tests for bug fixes or new behaviour.

## Security

Read [SECURITY.md](SECURITY.md) before reporting a vulnerability. This prototype must not be used with real payment credentials or physical access-control equipment.

## Licence

MIT. See [LICENSE](LICENSE).