import sqlite3
from typing import List, Dict, Any
# Importujeme funkcie, ktoré sme práve vytvorili
from repositories.matches import list_matches as repo_list_matches, insert_match as repo_insert_match, delete_match as repo_delete_match, update_score as repo_update_score

class MatchesService:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def get_all_matches(self) -> List[Dict[str, Any]]:
        return repo_list_matches(self.conn)

    def create_match(self, date: str, opponent: str, location: str, team_id: int = 1) -> int:
        # Prednastavené team_id=1, lebo predpokladáme, že hrá náš hlavný tím (FK Lokomotíva)
        return repo_insert_match(self.conn, date, opponent, location, team_id)

    def remove_match(self, match_id: int):
        repo_delete_match(self.conn, match_id)

    def set_score(self, match_id: int, home_goals: int, away_goals: int):
        repo_update_score(self.conn, match_id, home_goals, away_goals)