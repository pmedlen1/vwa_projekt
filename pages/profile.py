from fastapi import APIRouter, Depends, Request
from services.auth import User
from services.stats import StatsService
from services.players import PlayersService
from dependencies import get_conn, get_current_user, require_user, stats_service, players_service

router = APIRouter()



@router.get("/", name="profile_ui")
async def profile_ui(
    request: Request,
    user: User = Depends(require_user),
    stats_svc: StatsService = Depends(stats_service),
    players_svc: PlayersService = Depends(players_service)
):
    # Načítame detailné info o hráčovi (ak je to hráč)
    player_details = None
    stats = None

    if user.role == 'player':
        player_details = players_svc.get_player_by_id(user.id)
        stats = stats_svc.get_my_stats(user.id)

    return request.app.state.templates.TemplateResponse(
        "profile.html",
        {
            "request": request,
            "user": user,
            "player_details": player_details,
            "stats": stats
        },
    )