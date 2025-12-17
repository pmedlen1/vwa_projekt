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

# Získanie všetkých udalostí (zápasy + tréningy) pre hráča
def get_player_events(conn: sqlite3.Connection, player_id: int) -> List[Dict[str, Any]]:
    #   Zápasy
    matches = conn.execute(
        """
        SELECT 
            'match' as type, 
            m.id as event_id, 
            m.date, 
            'Zápas: ' || m.opponent as title, 
            a.confirmed, 
            a.present 
        FROM matches m
        LEFT JOIN attendance a ON m.id = a.match_id AND a.user_id = ?
        ORDER BY m.date DESC
        """,
        (player_id,)
    ).fetchall()

    # Tréningy
    trainings = conn.execute(
        """
        SELECT 
            'training' as type, 
            t.id as event_id, 
            t.date, 
            'Tréning: ' || t.location as title, 
            a.confirmed, 
            a.present 
        FROM trainings t
        LEFT JOIN attendance a ON t.id = a.training_id AND a.user_id = ?
        ORDER BY t.date DESC
        """,
        (player_id,)
    ).fetchall()

    # Spojíme a zoradíme podľa dátumu
    all_events = [dict(r) for r in matches] + [dict(r) for r in trainings]
    all_events.sort(key=lambda x: x['date'], reverse=True)

    return all_events

#  Nastavenie prítomnosti (present) - potvrdzuje tréner
def set_player_presence(conn: sqlite3.Connection, user_id: int, event_type: str, event_id: int, present: bool) -> None:
    # Zistíme, či záznam v attendance existuje
    if event_type == 'match':
        row = conn.execute("SELECT id FROM attendance WHERE user_id = ? AND match_id = ?", (user_id, event_id)).fetchone()
        col_name = 'match_id'
    else:
        row = conn.execute("SELECT id FROM attendance WHERE user_id = ? AND training_id = ?", (user_id, event_id)).fetchone()
        col_name = 'training_id'

    if row:
        conn.execute("UPDATE attendance SET present = ? WHERE id = ?", (present, row['id']))
    else:
        # Ak záznam neexistuje (hráč ani neklikol účasť), vytvoríme ho
        conn.execute(
            f"INSERT INTO attendance(user_id, {col_name}, present) VALUES (?, ?, ?)",
            (user_id, event_id, present)
        )
    conn.commit()