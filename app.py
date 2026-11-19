from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

app = Flask(__name__)
DB = Path(app.instance_path) / "bookings.db"
SERVICES = {
    "Haircut": (30, 20),
    "Skin fade": (45, 25),
    "Beard trim": (20, 12),
    "Hair + beard": (45, 30),
}
BARBERS = ["Charlie", "Sam"]

def db():
    DB.parent.mkdir(exist_ok=True)
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    with db() as con:
        con.execute("""CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service TEXT NOT NULL,
            barber TEXT NOT NULL,
            booking_date TEXT NOT NULL,
            booking_time TEXT NOT NULL,
            customer_name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(barber, booking_date, booking_time)
        )""")

def slots_for(date, barber):
    start = datetime.strptime("09:00", "%H:%M")
    end = datetime.strptime("16:00", "%H:%M")
    slots = []
    while start < end:
        slots.append(start.strftime("%H:%M"))
        start += timedelta(minutes=45)
    with db() as con:
        if barber == "Anyone":
            rows = con.execute("SELECT booking_time, COUNT(*) n FROM bookings WHERE booking_date=? GROUP BY booking_time", (date,)).fetchall()
            unavailable = {r["booking_time"] for r in rows if r["n"] >= len(BARBERS)}
        else:
            rows = con.execute("SELECT booking_time FROM bookings WHERE booking_date=? AND barber=?", (date, barber)).fetchall()
            unavailable = {r["booking_time"] for r in rows}
    return [s for s in slots if s not in unavailable]

@app.route("/")
def index():
    return render_template("index.html", services=SERVICES, barbers=BARBERS)

@app.get("/api/availability")
def availability():
    date = request.args.get("date", "")
    barber = request.args.get("barber", "Anyone")
    return jsonify(slots_for(date, barber) if date else [])

@app.post("/book")
def book():
    f = request.form
    requested_barber = f["barber"]
    candidates = BARBERS if requested_barber == "Anyone" else [requested_barber]
    chosen = None
    with db() as con:
        for barber in candidates:
            try:
                con.execute("INSERT INTO bookings(service,barber,booking_date,booking_time,customer_name,email,phone) VALUES(?,?,?,?,?,?,?)",
                            (f["service"], barber, f["date"], f["time"], f["name"], f["email"], f.get("phone", "")))
                chosen = barber
                break
            except sqlite3.IntegrityError:
                continue
    if not chosen:
        return "That slot has just been taken. Please choose another.", 409
    return redirect(url_for("confirmed", barber=chosen, date=f["date"], time=f["time"]))

@app.get("/confirmed")
def confirmed():
    return render_template("confirmed.html", barber=request.args.get("barber"), date=request.args.get("date"), time=request.args.get("time"))

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
