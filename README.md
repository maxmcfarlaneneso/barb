# Harris & Co. barber booking V1

A deliberately simple Flask + SQLite barber booking site with the booking flow on the homepage.

## Run locally

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000. The SQLite database is created in `instance/bookings.db`.

## Before using for a real shop

Replace the placeholder business/address/barber details. V1 uses 45-minute start intervals and simple fixed opening times. Add an owner/admin view and configurable opening hours before production use.
