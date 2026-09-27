import sqlite3
from pathlib import Path
from typing import Optional

class Database:
    def __init__(self, path: str = 'parksmart.db'):
        self.path = Path(path)
        self.conn = sqlite3.connect(self.path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute('PRAGMA foreign_keys = ON')
        self.create_schema()

    def create_schema(self):
        self.conn.executescript('''
        CREATE TABLE IF NOT EXISTS parking_slots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slot_number TEXT NOT NULL UNIQUE,
            status TEXT NOT NULL CHECK(status IN ('AVAILABLE','OCCUPIED'))
        );
        CREATE TABLE IF NOT EXISTS parking_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            registration TEXT NOT NULL,
            slot_id INTEGER NOT NULL,
            entry_time TEXT NOT NULL,
            exit_time TEXT,
            duration_minutes INTEGER,
            fee INTEGER,
            status TEXT NOT NULL CHECK(status IN ('ACTIVE','PAYMENT_PENDING','PAID','CANCELLED')),
            FOREIGN KEY(slot_id) REFERENCES parking_slots(id)
        );
        CREATE UNIQUE INDEX IF NOT EXISTS idx_one_active_vehicle
          ON parking_sessions(registration) WHERE status IN ('ACTIVE','PAYMENT_PENDING');
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL UNIQUE,
            amount INTEGER NOT NULL,
            paid_at TEXT NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('PAID','FAILED')),
            FOREIGN KEY(session_id) REFERENCES parking_sessions(id)
        );
        CREATE TABLE IF NOT EXISTS waiting_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            registration TEXT NOT NULL UNIQUE,
            requested_at TEXT NOT NULL
        );
        ''')
        self.conn.commit()

    def seed_slots(self, count: int = 10):
        existing = self.conn.execute('SELECT COUNT(*) c FROM parking_slots').fetchone()['c']
        for i in range(existing + 1, count + 1):
            self.conn.execute('INSERT INTO parking_slots(slot_number,status) VALUES (?,?)', (f'A{i:02d}', 'AVAILABLE'))
        self.conn.commit()

    def slots(self):
        return self.conn.execute('SELECT * FROM parking_slots ORDER BY id').fetchall()

    def close(self):
        self.conn.close()
