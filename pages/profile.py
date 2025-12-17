import sqlite3
from fastapi import APIRouter, Depends, Request
from services.auth import User
from services.stats import StatsService
from services.players import PlayersService
from repositories.users import get_user_by_id
from dependencies import get_conn, require_user, stats_service, players_service

router = APIRouter()

@router.get("/", name="profile_ui")
async def profile_ui(
    request: Request,
    current_user: User = Depends(require_user), #
    stats_svc: StatsService = Depends(stats_service),
    players_svc: PlayersService = Depends(players_service),
    conn: sqlite3.Connection = Depends(get_conn) # Potrebujeme DB spojenie
):
    full_user_data = get_user_by_id(conn, current_user.id)

    if not full_user_data:
        # Vytvoríme provizórny slovník z objektu User
        full_user_data = {
            "id": current_user.id,
            "username": current_user.username,
            "role": current_user.role,
            "first_name": "",
            "last_name": ""
        }

    # 2. Ak je to hráč, načítame aj štatistiky
    stats = None
    if full_user_data['role'] == 'player':
        stats = stats_svc.get_my_stats(full_user_data['id'])

    # 3. Renderujeme šablónu a posielame 'user' ako plný slovník dát
    return request.app.state.templates.TemplateResponse(
        "profile.html",
        {
            "request": request,
            "user": full_user_data, # <--- Tu posielame kompletné dáta
            "stats": stats
        },
    )