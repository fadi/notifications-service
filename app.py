from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from typing import Any, Dict

from flask import Flask, request, jsonify
from jinja2 import Template, StrictUndefined

DB_PATH = "audit_log.db"

# Predefined string templates (in real life these would be stored elsewhere)
TEMPLATES: Dict[str, str] = {
    "welcome": "Hi {{ name }}, welcome to {{ product }}!",
    "reset_password": "Hello {{ name }}, reset your password using this code: {{ code }}",
    "invoice_ready": "Hi {{ name }}, your invoice #{{ invoice_id }} is ready. Total: {{ total }}",
}

app = Flask(__name__)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    schema_sql = """
    CREATE TABLE IF NOT EXISTS recipient_preferences (
      recipient_id TEXT PRIMARY KEY,
      preferred_channel TEXT NOT NULL CHECK (preferred_channel IN ('SMS', 'Email'))
    );

    CREATE TABLE IF NOT EXISTS audit_log (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      recipient_id TEXT NOT NULL,
      template_name TEXT NOT NULL,
      channel TEXT NOT NULL CHECK (channel IN ('SMS', 'Email')),
      message TEXT NOT NULL,
      status TEXT NOT NULL,
      created_at TEXT NOT NULL
    );
    """
    with get_db() as conn:
        conn.executescript(schema_sql)

        # Optional seed data (safe to run repeatedly)
        conn.execute(
            "INSERT OR IGNORE INTO recipient_preferences (recipient_id, preferred_channel) VALUES (?, ?)",
            ("user_1", "Email"),
        )
        conn.execute(
            "INSERT OR IGNORE INTO recipient_preferences (recipient_id, preferred_channel) VALUES (?, ?)",
            ("user_2", "SMS"),
        )


def lookup_preference(recipient_id: str) -> str:
    """
    Mocked database lookup:
    - If recipient has a preference stored: return it
    - Otherwise default to Email
    """
    with get_db() as conn:
        row = conn.execute(
            "SELECT preferred_channel FROM recipient_preferences WHERE recipient_id = ?",
            (recipient_id,),
        ).fetchone()

    if row and row["preferred_channel"] in ("SMS", "Email"):
        return str(row["preferred_channel"])
    return "Email"


def render_template(template_name: str, variable_data: Dict[str, Any]) -> str:
    if template_name not in TEMPLATES:
        raise KeyError(f"Unknown template_name: {template_name}")

    template_str = TEMPLATES[template_name]
    tmpl = Template(template_str, undefined=StrictUndefined)
    return tmpl.render(**variable_data)


def write_audit_log(
    recipient_id: str,
    template_name: str,
    channel: str,
    message: str,
    status: str,
) -> int:
    created_at = utc_now_iso()
    with get_db() as conn:
        cur = conn.execute(
            """
            INSERT INTO audit_log (recipient_id, template_name, channel, message, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (recipient_id, template_name, channel, message, status, created_at),
        )
        log_id = int(cur.lastrowid)

    # Mock sending: print to console
    print(
        json.dumps(
            {
                "log_id": log_id,
                "recipient_id": recipient_id,
                "template_name": template_name,
                "channel": channel,
                "message": message,
                "status": status,
                "created_at": created_at,
            },
            ensure_ascii=False,
        )
    )
    return log_id


@app.route("/send", methods=["POST"])
def send_notification():
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 415

    payload = request.get_json(silent=True) or {}
    recipient_id = payload.get("recipient_id")
    template_name = payload.get("template_name")
    variable_data = payload.get("variable_data")

    if not isinstance(recipient_id, str) or not recipient_id.strip():
        return jsonify({"error": "recipient_id must be a non-empty string"}), 400
    if not isinstance(template_name, str) or not template_name.strip():
        return jsonify({"error": "template_name must be a non-empty string"}), 400
    if not isinstance(variable_data, dict):
        return jsonify({"error": "variable_data must be an object/dict"}), 400

    channel = lookup_preference(recipient_id)

    try:
        message = render_template(template_name, variable_data)
    except KeyError:
        return jsonify({"error": f"Unknown template_name '{template_name}'"}), 404
    except Exception as e:
        return jsonify({"error": f"Template render failed: {str(e)}"}), 400

    log_id = write_audit_log(
        recipient_id=recipient_id,
        template_name=template_name,
        channel=channel,
        message=message,
        status="queued",
    )

    return jsonify({"status": "queued", "log_id": log_id}), 200


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"ok": True}), 200


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5050, debug=True)
