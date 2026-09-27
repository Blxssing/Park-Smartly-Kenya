from app.database import Database
from app.parking import ParkingSystem
from datetime import datetime, timedelta

def main():
    db = Database('parksmart.db')
    db.seed_slots(10)
    system = ParkingSystem(db)
    print('ParkSmart Kenya - Console Demo')
    print('Available slots:', [s['slot_number'] for s in system.available_slots()])
    result = system.enter_vehicle('KDA123A')
    print('Entry:', result)
    now = datetime.now().replace(microsecond=0)
    exit_time = (now + timedelta(hours=2)).isoformat()
    exit_result = system.request_exit('KDA123A', exit_time)
    print('Exit:', exit_result)
    print('Payment:', system.pay_and_exit(exit_result['session_id']))
    db.close()

if __name__ == '__main__': main()
