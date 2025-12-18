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
            "matches": matches_with_attendance,
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
    errors = []
    if not opponent.strip():
        errors.append("Názov súpera je povinný.")
    if not location.strip():
        errors.append("Miesto zápasu je povinné.")
    if not date:
        errors.append("Dátum je povinný.")

    if errors:
        matches_list = svc.get_all_matches()
        return request.app.state.templates.TemplateResponse(
            "matches.html",
            {"request": request, "matches": matches_list, "user": user, "error": errors[0]},
            status_code=status.HTTP_400_BAD_REQUEST
        )

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
    home_score: Optional[str] = Form(None),
    away_score: Optional[str] = Form(None),
    svc: MatchesService = Depends(matches_service),
    user: User = Depends(require_admin_or_coach),
):

    if not opponent.strip() or not location.strip():
        match = svc.get_match(match_id)
        return request.app.state.templates.TemplateResponse(
            "edit_match.html",
            {"request": request, "match": match, "user": user, "error": "Všetky textové polia sú povinné."},
             status_code=status.HTTP_400_BAD_REQUEST
        )

    if (home_score is not None and home_score < 0) or (away_score is not None and away_score < 0):
        match = svc.get_match(match_id)
        return request.app.state.templates.TemplateResponse(
            "edit_match.html",
            {"request": request, "match": match, "user": user, "error": "Skóre nemôže byť záporné."},
             status_code=status.HTTP_400_BAD_REQUEST
        )

    # Konverzia: Ak je string prázdny, nastavíme None. Inak prevedieme na int.
    h_score_int = int(home_score) if home_score and home_score.strip() else None
    a_score_int = int(away_score) if away_score and away_score.strip() else None

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

# Endpoint pre správu zápasu (Detail pre Trénera)
@router.get("/{match_id}/manage", name="manage_match_ui")
async def manage_match_ui(
    request: Request,
    match_id: int,
    svc: MatchesService = Depends(matches_service),
    user: User = Depends(require_admin_or_coach),
):
    match = svc.get_match(match_id)
    if not match:
        return RedirectResponse(url=request.url_for("matches_ui"))

    participants = svc.get_match_participants(match_id)

    return request.app.state.templates.TemplateResponse(
        "manage_match.html",
        {
            "request": request,
            "match": match,
            "participants": participants,
            "user": user
        }
    )

# Endpoint pre hodnotenie hráča
@router.post("/{match_id}/evaluate/{player_id}", name="evaluate_player_post")
async def evaluate_player_post(
    request: Request,
    match_id: int,
    player_id: int,
    rating: float = Form(...),
    comment: str = Form(""),
    svc: MatchesService = Depends(matches_service),
    user: User = Depends(require_admin_or_coach),
):

    if not (0 <= rating <= 10):
        return RedirectResponse(
            url=request.url_for("manage_match_ui", match_id=match_id) + "?error=ZleHodnotenie",
            status_code=status.HTTP_303_SEE_OTHER
        )

    svc.save_evaluation(match_id, player_id, user.id, rating, comment)
    # Presmerujeme späť na stránku správy zápasu
    return RedirectResponse(
        url=request.url_for("manage_match_ui", match_id=match_id),
        status_code=status.HTTP_303_SEE_OTHER
    )

# Detail zápasu pre Hráča (Štatistiky)
@router.get("/{match_id}/detail", name="match_detail_ui")
async def match_detail_ui(
    request: Request,
    match_id: int,
    svc: MatchesService = Depends(matches_service),
    user: User = Depends(require_user), # Prístupné pre každého prihláseného
):
    match = svc.get_match(match_id)
    if not match:
        return RedirectResponse(url=request.url_for("matches_ui"))

    # Použijeme metódu get_match_participants, ktorá vráti hráčov aj s hodnoteniami
    participants = svc.get_match_participants(match_id)

    return request.app.state.templates.TemplateResponse(
        "match_detail.html",
        {
            "request": request,
            "match": match,
            "participants": participants,
            "user": user
        }
    )