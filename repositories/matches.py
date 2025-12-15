import sqlite3
from typing import List, Dict, Any, Optional

# 1. Získanie všetkých zápasov
def list_matches(conn: sqlite3.Connection) -> List[Dict[str, Any]]:
    # Spojíme tabuľku matches s teams, aby sme videli názov tímu súpera (ak by sme ho mali v db,
    # ale v tvojom návrhu je súper len text 'opponent', takže stačí jednoduchý select).
    # Vyberáme aj ID, aby sme mohli zápas zmazať.
    rows = conn.execute(
        """
        SELECT id, date, opponent, location, home_score, away_score 
        FROM matches 
        ORDER BY date DESC
        """
    ).fetchall()
    return [dict(r) for r in rows]

# 2. Vloženie nového zápasu
def insert_match(
    conn: sqlite3.Connection,
    date: str,
    opponent: str,
    location: str,
    team_id: int
) -> int:
    cur = conn.execute(
        "INSERT INTO matches(date, opponent, location, team_id) VALUES (?, ?, ?, ?)",
        (date, opponent, location, team_id),
    )
    conn.commit()
    return cur.lastrowid

# 3. Vymazanie zápasu
def delete_match(conn: sqlite3.Connection, match_id: int) -> None:
    conn.execute("DELETE FROM matches WHERE id = ?", (match_id,))
    conn.commit()

# 4. Aktualizácia skóre (pre trénera)
def update_score(conn: sqlite3.Connection, match_id: int, home: int, away: int) -> None:
    conn.execute(
        "UPDATE matches SET home_score = ?, away_score = ? WHERE id = ?",
        (home, away, match_id)
    )
    conn.commit()