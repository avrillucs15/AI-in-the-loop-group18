CREATE TABLE IF NOT EXISTS decisions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  guild_id INTEGER NOT NULL,
  channel_id INTEGER NOT NULL,
  thread_id INTEGER,
  message_id INTEGER,
  proposer_id INTEGER NOT NULL,
  question TEXT NOT NULL,
  deadline TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'open',
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS options (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  decision_id INTEGER NOT NULL REFERENCES decisions(id),
  label TEXT NOT NULL,
  text TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS stances (
  decision_id INTEGER NOT NULL REFERENCES decisions(id),
  user_id INTEGER NOT NULL,
  option_id INTEGER NOT NULL REFERENCES options(id),
  stance TEXT NOT NULL CHECK (stance IN ('support','reserved','oppose')),
  reason TEXT,
  anonymous INTEGER NOT NULL DEFAULT 1,
  updated_at TEXT NOT NULL,
  PRIMARY KEY (decision_id, user_id, option_id)
);
CREATE TABLE IF NOT EXISTS ai_summaries (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  decision_id INTEGER NOT NULL REFERENCES decisions(id),
  points_json TEXT NOT NULL,
  status TEXT NOT NULL,
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS conclusions (
  decision_id INTEGER PRIMARY KEY REFERENCES decisions(id),
  final_decision TEXT NOT NULL,
  resolution_note TEXT,
  concluded_at TEXT NOT NULL
);