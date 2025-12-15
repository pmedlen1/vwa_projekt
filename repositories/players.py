import sqlite3
from typing import List, Dict, Any, Optional

def list_players(conn: sqlite3.Connection) -> List[Dict[str, Any]]:
    rows = conn.execute(
        """
        SELECT * FROM users WHERE role = 'player' 
        ORDER BY last_name , first_name
        """
    ).fetchall()
    return [dict(r) for r in rows]

def get_player(conn: sqlite3.Connection, player_id: int) -> Optional[Dict[str, Any]]:
    row = conn.execute("SELECT * FROM users WHERE id = ? AND role = 'player'", (player_id,)).fetchone()
    return dict(row) if row else None

def insert_player(
        conn: sqlite3.Connection,
        username: str,
        password_hash: str,
        first_name: str,
        last_name: str,
        position: str,
        birth_date: str,
) -> int:
    cur = conn.execute(
        """
        INSERT INTO users (username, password_hash, role, first_name, last_name, position, birth_date)
        VALUES (?, ?, 'player', ?, ?, ?, ?)
        """,
        (username, password_hash, first_name, last_name, position, birth_date)
    )
    conn.commit()
    return cur.lastrowid

def update_player(
        conn: sqlite3.Connection,
        player_id: int,
        first_name: str,
        last_name: str,
        position: str,
        birth_date: str,
) -> None:
    conn.execute(
        """
        UPDATE users 
        SET first_name = ?, last_name = ?, position = ?, birth_date = ?
        WHERE id = ?
        """,
        (first_name, last_name, position, birth_date, player_id)\
    )
    conn.commit()

def delete_player(conn: sqlite3.Connection, player_id: int) -> None:
    conn.execute("DELETE FROM users WHERE id = ?", (player_id,))
    conn.commit()

