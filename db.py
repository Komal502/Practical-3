import sqlite3
from datetime import datetime
from typing import List, Dict, Any

DB = "webconf_lite.db"

def init_db():
    conn = sqlite3.connect(DB, check_same_thread=False)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS meetings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT,
            start_time TEXT,
            duration_minutes INTEGER,
            host TEXT,
            created_at TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS chat (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            meeting_id INTEGER,
            sender TEXT,
            message TEXT,
            ts TEXT
        )
    ''')
    conn.commit()
    return conn

_conn = init_db()

def create_meeting(title: str, description: str, start_time: str, duration: int, host: str):
    c = _conn.cursor()
    c.execute('''
        INSERT INTO meetings (title, description, start_time, duration_minutes, host, created_at)
        VALUES (?,?,?,?,?,?)
    ''', (title, description, start_time, duration, host, datetime.utcnow().isoformat()))
    _conn.commit()
    return c.lastrowid

def list_meetings() -> List[Dict[str, Any]]:
    c = _conn.cursor()
    c.execute('SELECT id, title, description, start_time, duration_minutes, host FROM meetings ORDER BY start_time')
    rows = c.fetchall()
    return [dict(id=r[0], title=r[1], description=r[2], start_time=r[3], duration_minutes=r[4], host=r[5]) for r in rows]

def add_chat(meeting_id: int, sender: str, message: str):
    c = _conn.cursor()
    c.execute('INSERT INTO chat (meeting_id, sender, message, ts) VALUES (?,?,?,?)', (meeting_id, sender, message, datetime.utcnow().isoformat()))
    _conn.commit()

def get_chat(meeting_id: int):
    c = _conn.cursor()
    c.execute('SELECT sender, message, ts FROM chat WHERE meeting_id=? ORDER BY id', (meeting_id,))
    return [{"sender": r[0], "message": r[1], "ts": r[2]} for r in c.fetchall()]
