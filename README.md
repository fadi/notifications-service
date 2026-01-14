––––––––––––––––––––––––––––––––––

Notifications Service (Mock)

Shared REST microservice for rendering notification templates and auditing simulated SMS/Email sends.

⸻

What this is

This service provides a single /send endpoint that accepts a JSON payload, renders a predefined template using variable data, determines whether the recipient prefers SMS or Email, and records the final message to a local SQLite database (audit_log.db) instead of actually sending it.

It acts as a centralised notification service for all group systems.

⸻

API Contract

POST /send

Request:
{
“recipient_id”: “user_123”,
“template_name”: “welcome”,
“variable_data”: {
“name”: “Fadi”,
“product”: “Sandpit.Space”
}
}

Success Response:
{
“status”: “queued”,
“log_id”: 1
}

⸻

Running Locally

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py

Service runs on:

http://127.0.0.1:5050

⸻

Health Check

curl http://127.0.0.1:5050/health

⸻

Templates (v1)

Available templates:

welcome
Variables: name, product

reset_password
Variables: name, code

invoice_ready
Variables: name, invoice_id, total

If a new template is needed, contact the Notifications module owner.

⸻

Database

SQLite file: audit_log.db
Schema defined in schema.sql

Tables:
recipient_preferences
audit_log

⸻

Notes

This service mocks sending behaviour. No real SMS or Email is sent. All messages are recorded for audit and debugging purposes.
––––––––––––––––––––––––––––––––––
