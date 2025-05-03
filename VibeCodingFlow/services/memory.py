
"""SQLite persistence layer for project specs and history."""

import sqlite3
import json
from pathlib import Path
from typing import Dict, Any, List

from platformdirs import user_data_path

APP_DATA_DIR = user_data_path("VibeCodingFlow")
APP_DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = APP_DATA_DIR / "vibe_db.sqlite"

_INIT_SQL = """
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    path TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS specs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    spec_json TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(project_id) REFERENCES projects(id)
);

CREATE TABLE IF NOT EXISTS history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    message TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(project_id) REFERENCES projects(id)
);
"""

def _conn():
    return sqlite3.connect(DB_PATH)


def init_db() -> None:
    with _conn() as conn:
        conn.executescript(_INIT_SQL)


# --- Projects -----------------------------------------------------------

def register_project(name: str, path: Path) -> int:
    with _conn() as conn:
        cur = conn.execute(
            "INSERT OR IGNORE INTO projects (name, path) VALUES (?, ?) RETURNING id",
            (name, str(path)),
        )
        row = cur.fetchone()
        if row and row[0]:
            return row[0]
        # Fallback if project existed
        cur = conn.execute("SELECT id FROM projects WHERE name = ?", (name,))
        return cur.fetchone()[0]


def get_project_path(name: str) -> Path:
    with _conn() as conn:
        cur = conn.execute("SELECT path FROM projects WHERE name = ?", (name,))
        row = cur.fetchone()
        if not row:
            raise KeyError(f"Unknown project {name!r}")
        return Path(row[0])


# --- Specs --------------------------------------------------------------

def save_spec(project_id: int, spec: Dict[str, Any]) -> None:
    with _conn() as conn:
        conn.execute(
            "INSERT INTO specs (project_id, spec_json) VALUES (?, ?)",
            (project_id, json.dumps(spec, ensure_ascii=False)),
        )


def get_last_spec(project_id: int) -> Dict[str, Any] | None:
    with _conn() as conn:
        cur = conn.execute(
            "SELECT spec_json FROM specs WHERE project_id = ? ORDER BY id DESC LIMIT 1",
            (project_id,),
        )
        row = cur.fetchone()
        return json.loads(row[0]) if row else None


# --- History ------------------------------------------------------------

def log_history(project_id: int, message: str) -> None:
    with _conn() as conn:
        conn.execute(
            "INSERT INTO history (project_id, message) VALUES (?, ?)",
            (project_id, message),
        )
