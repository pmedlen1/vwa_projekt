import sqlite3
from dataclasses import dataclass
from typing import Optional
from passlib.context import CryptContext
from repositories.users import get_user_by_username

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@dataclass
class User:
    id: int
    username: str
    role: str


class AuthService:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def authenticate(self, username: str, password: str) -> Optional[User]:
        user = get_user_by_username(self.conn, username)
        if not user:
            return None
        if not pwd_context.verify(password, user["password_hash"]):
            return None
        return User(id=user["id"], username=user["username"], role=user["role"])

    def hash_password(self, password: str) -> str:
        return pwd_context.hash(password)

