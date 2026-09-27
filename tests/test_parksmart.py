import tempfile
from datetime import datetime, timedelta
from app.datastructures import Stack, Queue
from app.database import Database
from app.parking import ParkingSystem


def make_system(n=2):
    tmp = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
    tmp.close()
    db = Database(tmp.name); db.seed_slots(n); return db, ParkingSystem(db)

def test_stack_lifo():
    s=Stack(); s.push(1); s.push(2); s.push(3)
    assert s.peek()==3 and s.pop()==3 and s.pop()==2 and s.pop()==1 and s.is_empty()

def test_queue_fifo():
    q=Queue(); q.enqueue('A'); q.enqueue('B'); assert q.dequeue()=='A'; assert q.dequeue()=='B'; assert q.is_empty()

def test_fee_boundaries():
    assert ParkingSystem.calculate_fee(0)==0
    assert ParkingSystem.calculate_fee(30)==0
    assert ParkingSystem.calculate_fee(31)==50
    assert ParkingSystem.calculate_fee(120)==50
    assert ParkingSystem.calculate_fee(121)==100
    assert ParkingSystem.calculate_fee(240)==100
    assert ParkingSystem.calculate_fee(241)==300
    assert ParkingSystem.calculate_fee(360)==300
    assert ParkingSystem.calculate_fee(361)==500

def test_negative_fee_rejected():
    import pytest
    with pytest.raises(ValueError): ParkingSystem.calculate_fee(-1)

def test_entry_assigns_slot():
    db,s=make_system(2); r=s.enter_vehicle('KDA123A','2026-09-28T08:00:00'); assert r['slot']=='A01'; assert db.slots()[0]['status']=='OCCUPIED'

def test_duplicate_vehicle_rejected():
    import pytest
    db,s=make_system(); s.enter_vehicle('KDA123A','2026-09-28T08:00:00')
    with pytest.raises(ValueError): s.enter_vehicle('KDA123A','2026-09-28T09:00:00')

def test_full_parking_queues_vehicle():
    db,s=make_system(1); s.enter_vehicle('A','2026-09-28T08:00:00'); r=s.enter_vehicle('B','2026-09-28T08:01:00'); assert r['queued'] is True

def test_duplicate_queue_rejected():
    import pytest
    db,s=make_system(1); s.enter_vehicle('A','2026-09-28T08:00:00'); s.enter_vehicle('B','2026-09-28T08:01:00')
    with pytest.raises(ValueError): s.enter_vehicle('B','2026-09-28T08:02:00')

def test_exit_calculates_duration_and_fee():
    db,s=make_system(); s.enter_vehicle('A','2026-09-28T08:00:00'); r=s.request_exit('A','2026-09-28T10:01:00'); assert r['duration_minutes']==121 and r['fee']==100

def test_slot_stays_occupied_until_payment():
    db,s=make_system(); s.enter_vehicle('A','2026-09-28T08:00:00'); r=s.request_exit('A','2026-09-28T10:00:00'); assert db.slots()[0]['status']=='OCCUPIED'; assert s.session(r['session_id'])['status']=='PAYMENT_PENDING'

def test_payment_opens_barrier_and_releases_slot():
    db,s=make_system(); s.enter_vehicle('A','2026-09-28T08:00:00'); r=s.request_exit('A','2026-09-28T10:00:00'); p=s.pay_and_exit(r['session_id'],'2026-09-28T10:01:00'); assert p['barrier']=='OPEN'; assert db.slots()[0]['status']=='AVAILABLE'; assert s.session(r['session_id'])['status']=='PAID'

def test_fifo_promotion():
    db,s=make_system(1); s.enter_vehicle('A','2026-09-28T08:00:00'); s.enter_vehicle('B','2026-09-28T08:01:00'); s.enter_vehicle('C','2026-09-28T08:02:00'); r=s.request_exit('A','2026-09-28T09:00:00'); p=s.pay_and_exit(r['session_id']); assert p['promoted']['registration']=='B'

def test_exit_before_entry_rejected():
    import pytest
    db,s=make_system(); s.enter_vehicle('A','2026-09-28T10:00:00')
    with pytest.raises(ValueError): s.request_exit('A','2026-09-28T09:00:00')
