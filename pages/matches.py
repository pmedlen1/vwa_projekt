from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from starlette import status
from services.matches import MatchesService
from services.auth import User
from dependencies import matches_service, get_current_user, require_admin, require_admin_or_coach, require_user

router = APIRouter()

@router.get("/", name="matches_ui")
async def matches_ui(
    request: Request,
    svc: MatchesService = Depends(matches_service),
    user: Optional[User] = Depends(get_current_user),
):
    # Získame zápasy cez service
    matches = svc.get_all_matches()

    matches_with_attendance = []
    if user and user.role == 'player':
        for m in matches:
            m_copy = dict(m)
            # Zavoláme service metódu get_player_attendance
            m_copy['attendance_confirmed'] = svc.get_player_attendance(user.id, m['id'])
            matches_with_attendance.append(m_copy)
    else:
        matches_with_attendance = matches

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

@router.get("/edit/{match_id}", name="edit_match_ui")
async def edit_match_ui(
    request: Request,
    match_id: int,
    svc: MatchesService = Depends(matches_service),
    user: User = Depends(require_admin_or_coach),
):
    match = svc.get_match(match_id)
    if not match:
        return RedirectResponse(url=request.url_for("matches_ui"))
    return request.app.state.templates.TemplateResponse(
        "edit_match.html",
        {"request": request, "match": match, "user": user}
    )

@router.post("/edit/{match_id}", name="edit_match_post")
async def edit_match_post(
    request: Request,
    match_id: int,
    opponent: str = Form(...),
    location: str = Form(...),
    date: str = Form(...),
    home_score: Optional[int] = Form(None),
    away_score: Optional[int] = Form(None),
    svc: MatchesService = Depends(matches_service),
    user: User = Depends(require_admin_or_coach),
):
    svc.update_match(match_id, date, opponent, location, home_score, away_score)
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

# Endpoint pre tlačidlo "Potvrdiť účasť"
@router.post("/attend/{match_id}", name="toggle_attendance_post")
async def toggle_attendance_post(
    request: Request,
    match_id: int,
    svc: MatchesService = Depends(matches_service),
    user: User = Depends(require_user), # Toto môže spustiť akýkoľvek prihlásený užívateľ (hráč)
):
    # Zistíme aktuálny stav
    current_status = svc.get_player_attendance(user.id, match_id)
    # A prepneme ho na opačný (ak potvrdil -> zruší, ak nie -> potvrdí)
    svc.confirm_attendance(user.id, match_id, not current_status)

    return RedirectResponse(url=request.url_for("matches_ui"), status_code=status.HTTP_303_SEE_OTHER)