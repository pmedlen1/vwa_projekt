import sqlite3
from typing import Any, Dict, Optional


def get_user_by_username(conn: sqlite3.Connection, username: str) -> Optional[Dict[str, Any]]:
    row = conn.execute(
        "SELECT id, username, password_hash, role FROM users WHERE username = ?",
        (username,),
    ).fetchone()
    return dict(row) if row else None


def insert_user(
    conn: sqlite3.Connection,
    username: str,
    password_hash: str,
    role: str,
) -> int:
    cur = conn.execute(
        "INSERT INTO users(username, password_hash, role) VALUES (?, ?, ?)",
        (username, password_hash, role),
    )
    conn.commit()
    return cur.lastrowid

