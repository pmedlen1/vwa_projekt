import sqlite3
from typing import Dict, Any

def get_player_stats(conn: sqlite3.Connection, player_id: int) -> Dict[str, Any]:
    # Počet odohraných zápasov (kde potvrdil účasť)
    matches_count = conn.execute(
        "SELECT COUNT(*) FROM attendance WHERE user_id = ? AND match_id IS NOT NULL AND confirmed = 1",
        (player_id,)
    ).fetchone()[0]

    # Počet tréningov (kde potvrdil účasť)
    trainings_count = conn.execute(
        "SELECT COUNT(*) FROM attendance WHERE user_id = ? AND training_id IS NOT NULL AND confirmed = 1",
        (player_id,)
    ).fetchone()[0]

    # Celkový počet naplánovaných zápasov
    total_matches = conn.execute("SELECT COUNT(*) FROM matches").fetchone()[0]

    #  Celkový počet naplánovaných tréningov
    total_trainings = conn.execute("SELECT COUNT(*) FROM trainings").fetchone()[0]

    return {
        "matches_attended": matches_count,
        "trainings_attended": trainings_count,
        "total_matches": total_matches,
        "total_trainings": total_trainings,
        "matches_percentage": round((matches_count / total_matches * 100) if total_matches > 0 else 0),
        "trainings_percentage": round((trainings_count / total_trainings * 100) if total_trainings > 0 else 0)
    }