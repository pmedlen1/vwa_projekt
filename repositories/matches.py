import sqlite3
from typing import List, Dict, Any, Optional

# Získanie všetkých zápasov
def list_matches(conn: sqlite3.Connection) -> List[Dict[str, Any]]:
    rows = conn.execute(
        """
        SELECT id, date, opponent, location, home_score, away_score 
        FROM matches 
        ORDER BY date DESC
        """
    ).fetchall()
    return [dict(r) for r in rows]

#  Vloženie nového zápasu
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

# Vymazanie zápasu
def delete_match(conn: sqlite3.Connection, match_id: int) -> None:
    # 1. Najprv vymažeme účasť spojenú s týmto zápasom
    conn.execute("DELETE FROM attendance WHERE match_id = ?", (match_id,))

    # 2. Potom vymažeme hodnotenia spojené s týmto zápasom
    # (Ak tabuľka evaluations existuje, pre istotu mažeme aj odtiaľ)
    conn.execute("DELETE FROM evaluations WHERE match_id = ?", (match_id,))

    # 3. Až nakoniec vymažeme samotný zápas
    conn.execute("DELETE FROM matches WHERE id = ?", (match_id,))

    conn.commit()

#  Aktualizácia skóre (pre trénera)
def update_score(conn: sqlite3.Connection, match_id: int, home: int, away: int) -> None:
    conn.execute(
        "UPDATE matches SET home_score = ?, away_score = ? WHERE id = ?",
        (home, away, match_id)
    )
    conn.commit()

# Získanie jedného zápasu podľa ID
def get_match(conn: sqlite3.Connection, match_id: int) -> Optional[Dict[str, Any]]:
    row = conn.execute(
        "SELECT * FROM matches WHERE id = ?",
        (match_id,)
    ).fetchone()
    return dict(row) if row else None

# Aktualizácia zápasu (skóre, dátum, miesto)
def update_match(
    conn: sqlite3.Connection,
    match_id: int,
    date: str,
    opponent: str,
    location: str,
    home_score: Optional[int],
    away_score: Optional[int]
) -> None:
    conn.execute(
        """
        UPDATE matches 
        SET date = ?, opponent = ?, location = ?, home_score = ?, away_score = ?
        WHERE id = ?
        """,
        (date, opponent, location, home_score, away_score, match_id)
    )
    conn.commit()

#   ÚČASŤ

def get_attendance(conn: sqlite3.Connection, user_id: int, match_id: int) -> Optional[Dict[str, Any]]:
    """
    Získa záznam o účasti pre daného používateľa a zápas.
    Vráti None, ak záznam neexistuje.
    """
    row = conn.execute(
        "SELECT * FROM attendance WHERE user_id = ? AND match_id = ?",
        (user_id, match_id)
    ).fetchone()
    return dict(row) if row else None

def set_attendance(conn: sqlite3.Connection, user_id: int, match_id: int, confirmed: bool) -> None:
    """
    Nastaví alebo aktualizuje stav účasti (potvrdenie).
    Ak záznam neexistuje, vytvorí ho. Ak existuje, aktualizuje stĺpec 'confirmed'.
    """
    existing = get_attendance(conn, user_id, match_id)

    if existing:
        conn.execute(
            "UPDATE attendance SET confirmed = ? WHERE id = ?",
            (confirmed, existing['id'])
        )
    else:
        conn.execute(
            "INSERT INTO attendance(user_id, match_id, confirmed) VALUES (?, ?, ?)",
            (user_id, match_id, confirmed)
        )
    conn.commit()

def get_match_attendees(conn: sqlite3.Connection, match_id: int) -> List[Dict[str, Any]]:
    """Vráti zoznam hráčov, ktorí potvrdili účasť na zápase."""
    rows = conn.execute(
        """
        SELECT u.id, u.first_name, u.last_name, u.position, a.confirmed
        FROM users u
        LEFT JOIN attendance a ON u.id = a.user_id AND a.match_id = ?
        WHERE u.role = 'player'
        ORDER BY u.last_name
        """,
        (match_id,)
    ).fetchall()
    return [dict(r) for r in rows]

#        HODNOTENIA

def get_evaluation(conn: sqlite3.Connection, match_id: int, player_id: int) -> Optional[Dict[str, Any]]:
    row = conn.execute(
        "SELECT * FROM evaluations WHERE match_id = ? AND player_id = ?",
        (match_id, player_id)
    ).fetchone()
    return dict(row) if row else None

def set_evaluation(conn: sqlite3.Connection, match_id: int, player_id: int, coach_id: int, rating: float, comment: str) -> None:
    existing = get_evaluation(conn, match_id, player_id)
    if existing:
        conn.execute(
            "UPDATE evaluations SET rating = ?, comment = ?, coach_id = ? WHERE id = ?",
            (rating, comment, coach_id, existing['id'])
        )
    else:
        conn.execute(
            "INSERT INTO evaluations(match_id, player_id, coach_id, rating, comment) VALUES (?, ?, ?, ?, ?)",
            (match_id, player_id, coach_id, rating, comment)
        )
    conn.commit()