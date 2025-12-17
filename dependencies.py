import sqlite3
from typing import Iterator, Optional
from fastapi import Depends, HTTPException, Request, status
from database.database import open_connection
from services.items import ItemsService
from services.auth import AuthService, User
from services.matches import MatchesService
from services.players import PlayersService
from services.session import session_store, SESSION_COOKIE_NAME
from services.stats import StatsService
from services.trainings import TrainingsService


def get_conn() -> Iterator[sqlite3.Connection]:
    with open_connection() as conn:
        yield conn

def items_service(conn: sqlite3.Connection = Depends(get_conn)) -> ItemsService:
    return ItemsService(conn)

def auth_service(conn: sqlite3.Connection = Depends(get_conn)) -> AuthService:
    return AuthService(conn)

def matches_service(conn: sqlite3.Connection = Depends(get_conn)) -> MatchesService:
    return MatchesService(conn)

def players_service(conn: sqlite3.Connection = Depends(get_conn)) -> PlayersService:
    return PlayersService(conn)

def trainings_service(conn = Depends(get_conn)) -> TrainingsService:
    return TrainingsService(conn)

def get_current_user(request: Request) -> Optional[User]:
    session_id = request.cookies.get(SESSION_COOKIE_NAME)
    return session_store.get_user(session_id)

def stats_service(conn = Depends(get_conn)) -> StatsService:
    return StatsService(conn)

def require_user(user: Optional[User] = Depends(get_current_user)) -> User:
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Login required")
    return user

def require_admin(user: User = Depends(require_user)) -> User:
    if user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return user

def require_admin_or_coach(user: User = Depends(require_user)) -> User:
    if user.role not in ("admin", "coach"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin or Coach access required")
    return user

def require_coach(user: User = Depends(require_user)) -> User:
    if user.role != "coach":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Coach access required")
    return user


