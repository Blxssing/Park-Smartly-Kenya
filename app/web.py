import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs

from .database import Database
from .parking import ParkingSystem
from .security import escape_html

DB_PATH = os.environ.get("PARKSMART_DB_PATH", "parksmart_web.db")
db = Database(DB_PATH)
db.seed_slots(10)
system = ParkingSystem(db)

# The demonstration shares one SQLite connection across request threads.
# Serialize operations on that connection; use per-handler messages.
db_lock = threading.RLock()

HTML = """<!doctype html><html><head><meta charset="utf-8"><title>ParkSmart Kenya</title><style>body{font-family:Arial;max-width:1000px;margin:40px auto;padding:0 20px}.slot{display:inline-block;padding:14px;margin:5px;border-radius:8px;background:#ddd}.available{background:#b9efc5}.occupied{background:#ffb8b8}form{margin:20px 0;padding:15px;border:1px solid #ddd}input,button{padding:9px;margin:4px}</style></head><body><h1>ParkSmart Kenya</h1><p>Local parking management demonstration</p><p><strong>Demo only:</strong> payments and barrier actions are simulated.</p><h2>Parking Slots</h2>{slots}<h2>Vehicle Entry</h2><form method="post"><input name="action" value="entry" type="hidden"><input name="registration" placeholder="KDA 123A" required><input name="time" placeholder="2026-09-28T08:00:00" required><button>Enter Vehicle</button></form><h2>Vehicle Exit</h2><form method="post"><input name="action" value="exit" type="hidden"><input name="registration" placeholder="KDA 123A" required><input name="time" placeholder="2026-09-28T10:00:00" required><button>Calculate Fee</button></form><h2>Payment simulation</h2><form method="post"><input name="action" value="pay" type="hidden"><input name="session_id" type="number" placeholder="Session ID" required><button>Simulate Payment &amp; Open Barrier</button></form><p>{message}</p></body></html>"""


class Handler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.message = ""
        super().__init__(*args, **kwargs)

    def _page(self):
        slots = "".join(
            "<span class='slot {}'>{} - {}</span>".format(
                "available" if slot["status"] == "AVAILABLE" else "occupied",
                escape_html(slot["slot_number"]),
                escape_html(slot["status"]),
            )
            for slot in db.slots()
        )
        page = HTML.replace("{slots}", slots).replace(
            "{message}", escape_html(self.message)
        )
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'none'; style-src 'unsafe-inline'; form-action 'self'; "
            "base-uri 'none'; frame-ancestors 'none'",
        )
        self.end_headers()
        self.wfile.write(page.encode("utf-8"))

    def do_GET(self):
        with db_lock:
            self._page()

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length < 0 or length > 16_384:
                raise ValueError("Request body is too large")
            body = self.rfile.read(length).decode("utf-8", errors="replace")
            data = {
                key: values[0]
                for key, values in parse_qs(body).items()
                if values
            }
            with db_lock:
                action = data.get("action")
                if action == "entry":
                    self.message = str(
                        system.enter_vehicle(
                            data.get("registration", ""), data.get("time") or None
                        )
                    )
                elif action == "exit":
                    self.message = str(
                        system.request_exit(
                            data.get("registration", ""), data.get("time", "")
                        )
                    )
                elif action == "pay":
                    self.message = str(
                        system.pay_and_exit(int(data.get("session_id", "")))
                    )
                else:
                    raise ValueError("Unknown action")
                self._page()
        except (ValueError, KeyError) as exc:
            self.message = f"ERROR: {exc}"
            with db_lock:
                self._page()
        except Exception:
            # Do not disclose internal exception details to a browser.
            self.message = "ERROR: The request could not be completed."
            with db_lock:
                self._page()


def run(host="127.0.0.1", port=8000):
    server = ThreadingHTTPServer((host, port), Handler)
    print(f"ParkSmart Kenya running at http://{host}:{port}")
    try:
        server.serve_forever()
    finally:
        server.server_close()


if __name__ == "__main__":
    run()
