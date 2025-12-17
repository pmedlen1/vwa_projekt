from fastapi import APIRouter, Depends, Request
from services.auth import User
from services.stats import StatsService
from services.users import UsersService
from dependencies import get_conn, get_current_user, require_user, stats_service, users_service

router = APIRouter()



@router.get("/", name="profile_ui")
async def profile_ui(
    request: Request,
    user: User = Depends(require_user),
    stats_svc: StatsService = Depends(stats_service),
    users_svc: UsersService = Depends(users_service),
):
    # Načítame detailné info o hráčovi (ak je to hráč)
    user_details = None
    stats = None

    user_details = users_svc.get_player_by_id(user.id)
    stats = stats_svc.get_my_stats(user.id)

    return request.app.state.templates.TemplateResponse(
        "profile.html",
        {
            "request": request,
            "user": user,
            "user_details": user_details,
            "stats": stats
        },
    )