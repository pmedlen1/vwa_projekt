import sqlite3
from typing import Dict, Any
from repositories.stats import get_player_stats as repo_get_player_stats

class StatsService:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def get_my_stats(self, user_id: int) -> Dict[str, Any]:
        return repo_get_player_stats(self.conn, user_id)