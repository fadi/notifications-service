# Notifications Service (Mock)

A small REST API that renders a notification template and writes an audit record to SQLite (no real sending).

## Run locally (macOS/Linux)
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
