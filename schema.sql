PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS parking_slots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slot_number TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL CHECK (status IN ('AVAILABLE', 'OCCUPIED'))
);

CREATE TABLE IF NOT EXISTS parking_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    registration TEXT NOT NULL,
    slot_id INTEGER NOT NULL,
    entry_time TEXT NOT NULL,
    exit_time TEXT,
    duration_minutes INTEGER,
    fee INTEGER,
    status TEXT NOT NULL CHECK (
        status IN ('ACTIVE', 'PAYMENT_PENDING', 'PAID', 'CANCELLED')
    ),
    FOREIGN KEY (slot_id) REFERENCES parking_slots(id)
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_one_active_vehicle
    ON parking_sessions(registration)
    WHERE status IN ('ACTIVE', 'PAYMENT_PENDING');

CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL UNIQUE,
    amount INTEGER NOT NULL,
    paid_at TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('PAID', 'FAILED')),
    FOREIGN KEY (session_id) REFERENCES parking_sessions(id)
);

CREATE TABLE IF NOT EXISTS waiting_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    registration TEXT NOT NULL UNIQUE,
    requested_at TEXT NOT NULL
);
