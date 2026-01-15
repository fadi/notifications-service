# Notifications Service (Mock) v1.0

Shared REST microservice for rendering notification templates and auditing simulated SMS/Email sends.

## What this is

This service provides a single /send endpoint that accepts a JSON payload, renders a predefined template using variable data, determines whether the recipient prefers SMS or Email, and records the final message to a local SQLite database (audit_log.db) instead of actually sending it.

It acts as a centralised notification service for all group systems.

This service is language-agnostic. Any system capable of making an HTTP request can integrate with it, regardless of programming language or framework.

## Who needs to install this?

Only teams who are running a local copy of the Notifications service need to install the dependencies listed in requirements.txt.

Teams that are simply calling the /send API from their own systems do not need to install anything — they only need to make an HTTP request to the running service.

## API Contract

Any module that needs to notify a user or staff member should make an HTTP POST request to the /send endpoint.

Your system does not need to implement email, SMS, or message formatting logic.

Instead, you send the required data to the Notifications service and it will:
	•	Choose Email or SMS based on stored user preference
	•	Render the final message using a predefined template
	•	Record a permanent audit log of the message

### POST /send

#### Request:
```json 
{
  "recipient_id": "user_123",
  "template_name": "welcome",
  "variable_data": {
    "name": "Fadi",
    "product": "Appointment Service"
  }
}
```
#### Success Response:
```json 
{
  "status": "queued",
  "log_id": 1
}
```
#### Example curl call: 
```bash 
curl -X POST http://127.0.0.1:5050/send \
  -H "Content-Type: application/json" \
  -d '{
    "recipient_id": "USER_12345",
    "template_name": "welcome",
    "variable_data": {
      "name": "Bruce",
      "product": "Health Matters"
    }
  }'
```
#### Running locally: 
```bash 
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```
#### Service runs on: 
```code
http://127.0.0.1:5050
```
#### Health check: 
```bash 
http://127.0.0.1:5050/health
```
#### Templates (v1)
Available templates:
	•	welcome
Variables: name, product
	•	reset_password
Variables: name, code
	•	invoice_ready
Variables: name, invoice_id, total

If a new template is needed, contact @fadi.

#### Databse:
SQLite file: audit_log.db
Schema defined in schema.sql

Tables:
	•	recipient_preferences
	•	audit_log

#### Notes
This service mocks sending behaviour. No real SMS or Email is sent. All messages are recorded for audit and debugging purposes.





