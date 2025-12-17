from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from starlette import status
from services.players import PlayersService
from services.auth import User
from dependencies import get_conn, get_current_user, require_admin_or_coach, players_service

router = APIRouter()


@router.get("/", name="players_ui")
async def players_ui(
    request: Request,
    svc: PlayersService = Depends(players_service),
    user: User = Depends(require_admin_or_coach),
):
    players = svc.get_all_players()
    return request.app.state.templates.TemplateResponse(
        "players.html",
        {"request": request, "players": players, "user": user},
    )

@router.get("/new", name="create_player_ui")
async def create_player_ui(
    request: Request,
    user: User = Depends(require_admin_or_coach)
):
    return request.app.state.templates.TemplateResponse(
        "edit_player.html",
        {"request": request, "player": None, "user": user, "errors": None}
    )

@router.post("/new", name="create_player_post")
async def create_player_post(
    request: Request,
    username: str = Form(...),
    first_name: str = Form(...),
    last_name: str = Form(...),
    position: str = Form(...),
    birth_date: str = Form(...),
    svc: PlayersService = Depends(players_service),
    user: User = Depends(require_admin_or_coach),
):
    try:
        svc.create_player(username, first_name, last_name, position, birth_date)
        return RedirectResponse(url=request.url_for("players_ui"), status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        print(f"CHYBA pri vytváraní hráča: {e}")
        return request.app.state.templates.TemplateResponse(
            "edit_player.html",
            {"request": request, "player": None, "user": user, "errors": {"global": str(e)}}
        )

@router.get("/edit/{player_id}", name="edit_player_ui")
async def edit_player_ui(
    request: Request,
    player_id: int,
    svc: PlayersService = Depends(players_service),
    user: User = Depends(require_admin_or_coach),
):
    player = svc.get_player_by_id(player_id)
    if not player:
        return RedirectResponse(url=request.url_for("players_ui"))

    return request.app.state.templates.TemplateResponse(
        "edit_player.html",
        {"request": request, "player": player, "user": user, "errors": None}
    )

@router.post("/edit/{player_id}", name="edit_player_post")
async def edit_player_post(
    request: Request,
    player_id: int,
    first_name: str = Form(...),
    last_name: str = Form(...),
    position: str = Form(...),
    birth_date: str = Form(...),
    svc: PlayersService = Depends(players_service),
    user: User = Depends(require_admin_or_coach),
):
    try:
        svc.update_player_info(player_id, first_name, last_name, position, birth_date)
        return RedirectResponse(url=request.url_for("players_ui"), status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        print(f"CHYBA pri úprave hráča {player_id}: {e}")
        player = svc.get_player_by_id(player_id)
        return request.app.state.templates.TemplateResponse(
            "edit_player.html",
            {"request": request, "player": player, "user": user, "errors": {"global": str(e)}}
        )

@router.post("/delete/{player_id}", name="delete_player_post")
async def delete_player_post(
    request: Request,
    player_id: int,
    svc: PlayersService = Depends(players_service),
    user: User = Depends(require_admin_or_coach),
):
    svc.remove_player(player_id)
    return RedirectResponse(url=request.url_for("players_ui"), status_code=status.HTTP_303_SEE_OTHER)

# NOVÉ: Zoznam účastí pre konkrétneho hráča (Tréner)
@router.get("/{player_id}/attendance", name="player_attendance_ui")
async def player_attendance_ui(
    request: Request,
    player_id: int,
    svc: PlayersService = Depends(players_service),
    user: User = Depends(require_admin_or_coach),
):
    player = svc.get_player_by_id(player_id)
    if not player:
        return RedirectResponse(url=request.url_for("players_ui"))

    events = svc.get_events_for_player(player_id)

    return request.app.state.templates.TemplateResponse(
        "player_attendance.html",
        {
            "request": request,
            "player": player,
            "events": events,
            "user": user
        }
    )

# NOVÉ: Potvrdenie prítomnosti (Tréner klikne)
@router.post("/{player_id}/attendance/{event_type}/{event_id}", name="toggle_presence_post")
async def toggle_presence_post(
    request: Request,
    player_id: int,
    event_type: str,
    event_id: int,
    svc: PlayersService = Depends(players_service),
    user: User = Depends(require_admin_or_coach),
):
    form = await request.form()

    present_value = form.get("present")
    # Ak je value "1", nastavujeme True (prítomný), inak False
    is_present = True if present_value == "1" else False

    svc.confirm_presence(player_id, event_type, event_id, is_present)

    return RedirectResponse(
        url=request.url_for("player_attendance_ui", player_id=player_id),
        status_code=status.HTTP_303_SEE_OTHER
    )