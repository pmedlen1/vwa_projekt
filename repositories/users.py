import sqlite3
from typing import Any, Dict, List, Optional

def get_user_by_username(conn: sqlite3.Connection, username: str) -> Optional[Dict[str, Any]]:
    row = conn.execute(
        "SELECT id, username, password_hash, role, first_name, last_name FROM users WHERE username = ?",
        (username,),
    ).fetchone()
    return dict(row) if row else None

def get_user_by_id(conn: sqlite3.Connection, user_id: int) -> Optional[Dict[str, Any]]:
    row = conn.execute(
        "SELECT * FROM users WHERE id = ?",
        (user_id,),
    ).fetchone()
    return dict(row) if row else None

def get_all_users(conn: sqlite3.Connection) -> List[Dict[str, Any]]:
    rows = conn.execute(
        "SELECT * FROM users ORDER BY role, last_name, first_name"
    ).fetchall()
    return [dict(r) for r in rows]

def insert_user(
    conn: sqlite3.Connection,
    username: str,
    password_hash: str,
    role: str,
    first_name: str = None,
    last_name: str = None,
    position: str = None,
    birth_date: str = None
) -> int:
    cur = conn.execute(
        """
        INSERT INTO users(username, password_hash, role, first_name, last_name, position, birth_date) 
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (username, password_hash, role, first_name, last_name, position, birth_date),
    )
    conn.commit()
    return cur.lastrowid

def update_user(
    conn: sqlite3.Connection,
    user_id: int,
    role: str,
    first_name: str,
    last_name: str,
    position: str = None,
    birth_date: str = None
) -> None:
    conn.execute(
        """
        UPDATE users 
        SET role = ?, first_name = ?, last_name = ?, position = ?, birth_date = ?
        WHERE id = ?
        """,
        (role, first_name, last_name, position, birth_date, user_id)
    )
    conn.commit()

def delete_user(conn: sqlite3.Connection, user_id: int) -> None:
    conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()