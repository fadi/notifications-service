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

INSERT OR IGNORE INTO recipient_preferences (recipient_id, preferred_channel) VALUES
  ('user_1', 'Email'),
  ('user_2', 'SMS');
