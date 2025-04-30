import sqlite3
import json
from pathlib import Path

import sqlite3
import json
from pathlib import Path

# теперь БД всегда одна — в папке самого пакета
DB_PATH = Path(__file__).parent.parent / ".vibe_db.sqlite"

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            path TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
            action TEXT NOT NULL,
            details TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(project_id) REFERENCES projects(id)
        );
        """)

def register_project(name: str, path: str) -> int:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('INSERT OR REPLACE INTO projects(name,path) VALUES(?,?)', (name, path))
        conn.commit()
        cur = conn.execute('SELECT id FROM projects WHERE name=?', (name,))
        return cur.fetchone()[0]

def update_project_path(name: str, path: str):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('UPDATE projects SET path=? WHERE name=?', (path, name))
        conn.commit()

def get_project_path(name: str) -> str | None:
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute('SELECT path FROM projects WHERE name=?', (name,))
        row = cur.fetchone()
    return row[0] if row else None

def save_spec(project_id: int, spec: dict):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            'INSERT INTO specs(project_id, spec_json) VALUES(?,?)',
            (project_id, json.dumps(spec, ensure_ascii=False))
        )
        conn.commit()

def log_history(project_id: int, action: str, details: dict):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            'INSERT INTO history(project_id, action, details) VALUES(?,?,?)',
            (project_id, action, json.dumps(details, ensure_ascii=False))
        )
        conn.commit()

def save_project_to_memory(name: str, spec: dict):
    """Сохраняет структуру проекта в базу данных."""
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute('SELECT id FROM projects WHERE name=?', (name,))
        row = cur.fetchone()
        if row:
            project_id = row[0]
            conn.execute(
                'INSERT INTO specs(project_id, spec_json) VALUES(?,?)',
                (project_id, json.dumps(spec, ensure_ascii=False))
            )
            conn.commit()
        else:
            raise ValueError(f"Проект '{name}' не найден в базе данных.")

def load_project_from_memory(name: str) -> dict | None:
    """Загружает последнюю версию структуры проекта из базы данных."""
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute('''
            SELECT spec_json FROM specs
            INNER JOIN projects ON specs.project_id = projects.id
            WHERE projects.name=?
            ORDER BY specs.timestamp DESC
            LIMIT 1
        ''', (name,))
        row = cur.fetchone()
    if row:
        return json.loads(row[0])
    return None
