# ParkSmart Kenya

A functional Python web-based parking management system for the DSA Task One requirements.

## Requirements covered
- Visual parking-slot availability before entry.
- Vehicle arrival/entry records.
- Automatic parking-duration calculation.
- Fee calculation using the assignment tariff.
- Payment-gated barrier opening.
- Dynamic SQLite database.
- Stack (LIFO), Queue (FIFO), and list/dictionary-style database access.
- Well-commented, modular Python code.
- Web interface.

## Tariff
- Up to 30 minutes: KSh 0
- Up to 2 hours: KSh 50
- Up to 4 hours: KSh 100
- Up to 6 hours: KSh 300
- Over 6 hours: KSh 500

## Run
```bash
python -m pytest -q
python main.py
python -m app.web
```
Then open http://127.0.0.1:8000
