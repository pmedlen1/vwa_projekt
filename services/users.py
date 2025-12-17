import sqlite3
from typing import List, Dict, Any, Optional
from passlib.context import CryptContext
from repositories.users import (
    get_all_users as repo_get_all_users,
    get_user_by_id as repo_get_user_by_id,
    insert_user as repo_insert_user,
    update_user as repo_update_user,
    delete_user as repo_delete_user
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UsersService:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def get_all_users(self) -> List[Dict[str, Any]]:
        return repo_get_all_users(self.conn)

    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        return repo_get_user_by_id(self.conn, user_id)

    def create_user(self, username: str, password: str, role: str, first_name: str, last_name: str, position: str = None, birth_date: str = None) -> int:
        password_hash = pwd_context.hash(password)
        return repo_insert_user(self.conn, username, password_hash, role, first_name, last_name, position, birth_date)

    def update_user(self, user_id: int, role: str, first_name: str, last_name: str, position: str = None, birth_date: str = None):
        # Poznámka: Heslo sa tu neaktualizuje, na to by bol potrebný osobitný endpoint alebo logika
        repo_update_user(self.conn, user_id, role, first_name, last_name, position, birth_date)

    def remove_user(self, user_id: int):
        repo_delete_user(self.conn, user_id)