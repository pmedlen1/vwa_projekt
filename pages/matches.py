from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from starlette import status
from services.matches import MatchesService
from services.auth import User
from dependencies import matches_service, get_current_user, require_admin, require_admin_or_coach

router = APIRouter()

@router.get("/", name="matches_ui")
async def matches_ui(
    request: Request,
    svc: MatchesService = Depends(matches_service),
    user: Optional[User] = Depends(get_current_user),
):
    # Získame zápasy cez service
    matches = svc.get_all_matches()

    return request.app.state.templates.TemplateResponse(
        "matches.html",
        {
            "request": request,
            "matches": matches,
            "user": user
        },
    )

@router.post("/new", name="create_match_post")
async def create_match_post(
    request: Request,
    opponent: str = Form(...),
    location: str = Form(...),
    date: str = Form(...), # Príde ako string z HTML <input type="datetime-local">
    svc: MatchesService = Depends(matches_service),
    user: User = Depends(require_admin_or_coach), # Len admin (a tréner) môže pridať zápas
):
    # Vytvoríme zápas
    svc.create_match(date=date, opponent=opponent, location=location)

    # Presmerujeme späť na zoznam zápasov
    return RedirectResponse(url=request.url_for("matches_ui"), status_code=status.HTTP_303_SEE_OTHER)

@router.post("/delete/{match_id}", name="delete_match_post")
async def delete_match_post(
    request: Request,
    match_id: int,
    svc: MatchesService = Depends(matches_service),
    user: User = Depends(require_admin_or_coach),
):
    svc.remove_match(match_id)
    return RedirectResponse(url=request.url_for("matches_ui"), status_code=status.HTTP_303_SEE_OTHER)