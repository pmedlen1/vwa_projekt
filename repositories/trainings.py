import sqlite3
from typing import List, Dict, Any, Optional

def list_trainings(conn: sqlite3.Connection) -> List[Dict[str, Any]]:

    rows = conn.execute(
        """
        SELECT id, date, location, description 
        FROM trainings 
        ORDER BY date DESC
        """
    ).fetchall()
    return [dict(r) for r in rows]

def get_training(conn: sqlite3.Connection, training_id: int) -> Optional[Dict[str, Any]]:
    row = conn.execute(
        "SELECT * FROM trainings WHERE id = ?",
        (training_id,)
    ).fetchone()
    return dict(row) if row else None

#       PRIDANIE TRENINGU

def insert_training(
    conn: sqlite3.Connection,
    date: str,
    location: str,
    description: str,
    team_id: int
) -> int:
    cur = conn.execute(
        "INSERT INTO trainings(date, location, description, team_id) VALUES (?, ?, ?, ?)",
        (date, location, description, team_id),
    )
    conn.commit()
    return cur.lastrowid

def update_training(
    conn: sqlite3.Connection,
    training_id: int,
    date: str,
    location: str,
    description: str
) -> None:
    conn.execute(
        "UPDATE trainings SET date = ?, location = ?, description = ? WHERE id = ?",
        (date, location, description, training_id)
    )
    conn.commit()

def delete_training(conn: sqlite3.Connection, training_id: int) -> None:
    conn.execute("DELETE FROM trainings WHERE id = ?", (training_id,))
    conn.commit()

#            UCAST NA TRENINGU

def get_training_attendance(conn: sqlite3.Connection, user_id: int, training_id: int) -> Optional[Dict[str, Any]]:
    row = conn.execute(
        "SELECT * FROM attendance WHERE user_id = ? AND training_id = ?",
        (user_id, training_id)
    ).fetchone()
    return dict(row) if row else None

def set_training_attendance(conn: sqlite3.Connection, user_id: int, training_id: int, confirmed: bool) -> None:
    existing = get_training_attendance(conn, user_id, training_id)

    if existing:
        conn.execute(
            "UPDATE attendance SET confirmed = ? WHERE id = ?",
            (confirmed, existing['id'])
        )
    else:
        conn.execute(
            "INSERT INTO attendance(user_id, training_id, confirmed) VALUES (?, ?, ?)",
            (user_id, training_id, confirmed)
        )
    conn.commit()