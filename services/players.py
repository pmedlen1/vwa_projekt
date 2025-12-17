import sqlite3
from typing import List, Dict, Any, Optional
from passlib.context import CryptContext
from repositories.players import (list_players as repo_list_players, get_player as repo_get_player,
                                  insert_player as repo_insert_player, update_player as repo_update_player,
                                  delete_player as repo_delete_player)

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

class PlayersService:
    def __init__(self, conn : sqlite3.Connection):
        self.conn = conn

    def get_all_players(self) -> List[Dict[str, Any]]:
        return repo_list_players(self.conn)

    def get_player_by_id(self, player_id: int) -> Optional[Dict[str, Any]]:
        return repo_get_player(self.conn, player_id)

    def create_player(self, username: str, first_name: str, last_name: str,
                      position: str, birth_date: str,) -> int:
        default_password = "hrac123"
        password = pwd_context.hash(default_password)
        return repo_insert_player(self.conn, username, password, first_name, last_name, position, birth_date)

    def update_player_info(self, player_id: int, first_name: str, last_name: str, position: str, birth_date: str ):
        repo_update_player(self.conn, player_id, first_name, last_name, position, birth_date)

    def delete_player(self, player_id: int):
        repo_delete_player(self.conn, player_id)
