from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse
from .database import Database
from .parking import ParkingSystem

DB_PATH = 'parksmart_web.db'
db = Database(DB_PATH)
db.seed_slots(10)
system = ParkingSystem(db)

HTML = '''<!doctype html><html><head><meta charset="utf-8"><title>ParkSmart Kenya</title><style>body{font-family:Arial;max-width:1000px;margin:40px auto;padding:0 20px} .slot{display:inline-block;padding:14px;margin:5px;border-radius:8px;background:#ddd}.available{background:#b9efc5}.occupied{background:#ffb8b8}form{margin:20px 0;padding:15px;border:1px solid #ddd}input,button{padding:9px;margin:4px}</style></head><body><h1>ParkSmart Kenya</h1><p>Modern parking management system</p><h2>Parking Slots</h2>{slots}<h2>Vehicle Entry</h2><form method="post"><input name="action" value="entry" type="hidden"><input name="registration" placeholder="KDA 123A" required><input name="time" placeholder="2026-09-28T08:00:00" required><button>Enter Vehicle</button></form><h2>Vehicle Exit</h2><form method="post"><input name="action" value="exit" type="hidden"><input name="registration" placeholder="KDA 123A" required><input name="time" placeholder="2026-09-28T10:00:00" required><button>Calculate Fee</button></form><h2>Payment</h2><form method="post"><input name="action" value="pay" type="hidden"><input name="session_id" type="number" placeholder="Session ID" required><button>Pay & Open Barrier</button></form><p>{message}</p></body></html>'''

class Handler(BaseHTTPRequestHandler):
    message = ''
    def _page(self):
        slots=''.join(f"<span class='slot {'available' if s['status']=='AVAILABLE' else 'occupied'}'>{s['slot_number']} - {s['status']}</span>" for s in db.slots())
        data=HTML.replace('{slots}', slots).replace('{message}', self.message)
        self.send_response(200); self.send_header('Content-Type','text/html; charset=utf-8'); self.end_headers(); self.wfile.write(data.encode())
    def do_GET(self): self._page()
    def do_POST(self):
        length=int(self.headers.get('Content-Length','0')); body=self.rfile.read(length).decode(); data={k:v[0] for k,v in parse_qs(body).items()}
        try:
            if data['action']=='entry': self.message=str(system.enter_vehicle(data['registration'],data['time']))
            elif data['action']=='exit': self.message=str(system.request_exit(data['registration'],data['time']))
            elif data['action']=='pay': self.message=str(system.pay_and_exit(int(data['session_id'])))
        except Exception as e: self.message=f'ERROR: {e}'
        self._page()

def run(host='127.0.0.1', port=8000):
    server=ThreadingHTTPServer((host,port),Handler); print(f'ParkSmart Kenya running at http://{host}:{port}'); server.serve_forever()

if __name__=='__main__': run()
