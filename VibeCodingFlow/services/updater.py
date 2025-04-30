import json
import sqlite3
from pathlib import Path
from .memory import DB_PATH

def get_last_spec(project_name: str) -> dict:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.execute('SELECT id FROM projects WHERE name=?', (project_name,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return {}
    pid = row[0]
    cur = conn.execute(
        'SELECT spec_json FROM specs WHERE project_id=? ORDER BY timestamp DESC LIMIT 1',
        (pid,)
    )
    row2 = cur.fetchone()
    conn.close()
    return json.loads(row2[0]) if row2 else {}

def diff_specs(old_spec: dict, new_spec: dict) -> list[str]:
    old_files = old_spec.get('project_structure', {})
    new_files = new_spec.get('project_structure', {})
    changed = []
    for path, desc in new_files.items():
        if path not in old_files or old_files[path] != desc:
            changed.append(path)
    return changed
