import sqlite3
from pathlib import Path

import pytest

from app.database import Database
from app.parking import ParkingSystem
from app.security import escape_html


def test_waiting_queue_is_restored_after_database_reopen(tmp_path):
    database_path = tmp_path / "parking.db"
    db = Database(str(database_path))
    db.seed_slots(1)
    system = ParkingSystem(db)

    system.enter_vehicle("KCA001A", "2026-09-28T08:00:00")
    queued = system.enter_vehicle("KCB002B", "2026-09-28T08:01:00")
    assert queued["queued"] is True
    db.close()

    reopened_db = Database(str(database_path))
    reopened_system = ParkingSystem(reopened_db)
    assert reopened_system.waiting.size() == 1
    assert reopened_system.waiting.peek() == "KCB002B"
    reopened_db.close()


def test_database_rejects_invalid_slot_status(tmp_path):
    db = Database(str(tmp_path / "parking.db"))
    with pytest.raises(sqlite3.IntegrityError):
        db.conn.execute(
            "INSERT INTO parking_slots(slot_number, status) VALUES (?, ?)",
            ("BAD-1", "BROKEN"),
        )
    db.close()


def test_database_enforces_one_active_session_per_registration(tmp_path):
    db = Database(str(tmp_path / "parking.db"))
    db.seed_slots(2)
    system = ParkingSystem(db)
    system.enter_vehicle("KDA123A", "2026-09-28T08:00:00")

    with pytest.raises(sqlite3.IntegrityError):
        with db.conn:
            db.conn.execute(
                """INSERT INTO parking_sessions
                   (registration, slot_id, entry_time, status)
                   VALUES (?, ?, ?, ?)""",
                ("KDA123A", 2, "2026-09-28T08:05:00", "ACTIVE"),
            )
    db.close()


def test_standalone_schema_enables_foreign_keys():
    connection = sqlite3.connect(":memory:")
    connection.executescript(Path("schema.sql").read_text(encoding="utf-8"))

    with pytest.raises(sqlite3.IntegrityError):
        connection.execute(
            "INSERT INTO payments(session_id, amount, paid_at, status) "
            "VALUES (999, 100, '2026-09-28T10:00:00', 'PAID')"
        )
    connection.close()


def test_html_escaping_blocks_markup_in_user_supplied_values():
    assert escape_html('<script>alert("x")</script>') == (
        "&lt;script&gt;alert(&quot;x&quot;)&lt;/script&gt;"
    )


def test_html_escaping_handles_non_string_values():
    assert escape_html(42) == "42"
