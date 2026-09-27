from datetime import datetime
from .datastructures import Stack, Queue

class ParkingSystem:
    def __init__(self, db):
        self.db = db
        self.history = Stack()
        self.waiting = Queue()
        self._load_waiting_queue()

    @staticmethod
    def parse_time(value):
        return datetime.fromisoformat(value)

    @staticmethod
    def calculate_fee(minutes: int) -> int:
        if minutes < 0:
            raise ValueError('Parking duration cannot be negative')
        if minutes <= 30:
            return 0
        if minutes <= 120:
            return 50
        if minutes <= 240:
            return 100
        if minutes <= 360:
            return 300
        return 500

    def _load_waiting_queue(self):
        for row in self.db.conn.execute('SELECT registration FROM waiting_queue ORDER BY id'):
            self.waiting.enqueue(row['registration'])

    def available_slots(self):
        return self.db.conn.execute("SELECT * FROM parking_slots WHERE status='AVAILABLE' ORDER BY id").fetchall()

    def _active(self, registration):
        return self.db.conn.execute("SELECT * FROM parking_sessions WHERE registration=? AND status IN ('ACTIVE','PAYMENT_PENDING')", (registration.upper(),)).fetchone()

    def _queued(self, registration):
        return self.db.conn.execute('SELECT * FROM waiting_queue WHERE registration=?', (registration.upper(),)).fetchone()

    def enter_vehicle(self, registration: str, entry_time: str | None = None):
        registration = registration.strip().upper()
        if not registration:
            raise ValueError('Registration number is required')
        if self._active(registration):
            raise ValueError('Vehicle is already inside the parking area')
        if self._queued(registration):
            raise ValueError('Vehicle is already in the waiting queue')
        slot = self.available_slots()
        if not slot:
            timestamp = entry_time or datetime.now().isoformat(timespec='seconds')
            self.db.conn.execute('INSERT INTO waiting_queue(registration,requested_at) VALUES (?,?)', (registration, timestamp))
            self.db.conn.commit()
            self.waiting.enqueue(registration)
            self.history.push(('WAITING', registration))
            return {'queued': True, 'registration': registration}
        timestamp = entry_time or datetime.now().isoformat(timespec='seconds')
        with self.db.conn:
            self.db.conn.execute('UPDATE parking_slots SET status=\'OCCUPIED\' WHERE id=?', (slot[0]['id'],))
            cur = self.db.conn.execute('''INSERT INTO parking_sessions(registration,slot_id,entry_time,status) VALUES (?,?,?,?)''', (registration, slot[0]['id'], timestamp, 'ACTIVE'))
        self.history.push(('ENTRY', registration, slot[0]['slot_number']))
        return {'queued': False, 'registration': registration, 'slot': slot[0]['slot_number'], 'session_id': cur.lastrowid}

    def request_exit(self, registration: str, exit_time: str):
        registration = registration.strip().upper()
        row = self._active(registration)
        if not row:
            raise ValueError('Vehicle is not currently parked')
        entry = self.parse_time(row['entry_time'])
        exit_dt = self.parse_time(exit_time)
        minutes = int((exit_dt - entry).total_seconds() // 60)
        if minutes < 0:
            raise ValueError('Exit time cannot be earlier than entry time')
        fee = self.calculate_fee(minutes)
        with self.db.conn:
            self.db.conn.execute('UPDATE parking_sessions SET exit_time=?,duration_minutes=?,fee=?,status=\'PAYMENT_PENDING\' WHERE id=?', (exit_time, minutes, fee, row['id']))
        self.history.push(('EXIT_REQUEST', registration, minutes, fee))
        return {'session_id': row['id'], 'registration': registration, 'duration_minutes': minutes, 'fee': fee}

    def pay_and_exit(self, session_id: int, paid_at: str | None = None):
        row = self.db.conn.execute('SELECT * FROM parking_sessions WHERE id=? AND status=\'PAYMENT_PENDING\'', (session_id,)).fetchone()
        if not row:
            raise ValueError('Session is not awaiting payment')
        paid_at = paid_at or datetime.now().isoformat(timespec='seconds')
        with self.db.conn:
            self.db.conn.execute('INSERT INTO payments(session_id,amount,paid_at,status) VALUES (?,?,?,\'PAID\')', (session_id, row['fee'], paid_at))
            self.db.conn.execute('UPDATE parking_sessions SET status=\'PAID\' WHERE id=?', (session_id,))
            self.db.conn.execute('UPDATE parking_slots SET status=\'AVAILABLE\' WHERE id=?', (row['slot_id'],))
        self.history.push(('PAYMENT', row['registration'], row['fee']))
        promoted = self._promote_next_vehicle()
        return {'barrier': 'OPEN', 'registration': row['registration'], 'amount': row['fee'], 'promoted': promoted}

    def _promote_next_vehicle(self):
        row = self.db.conn.execute('SELECT * FROM waiting_queue ORDER BY id LIMIT 1').fetchone()
        if not row or not self.available_slots():
            return None
        registration = row['registration']
        self.db.conn.execute('DELETE FROM waiting_queue WHERE id=?', (row['id'],))
        self.waiting.dequeue()
        result = self.enter_vehicle(registration)
        self.db.conn.commit()
        return result

    def session(self, session_id):
        return self.db.conn.execute('SELECT * FROM parking_sessions WHERE id=?', (session_id,)).fetchone()
