from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Request
import sqlite3
from starlette.responses import RedirectResponse
from services.auth import User
from services.matches import MatchesService
from services.players import PlayersService
from services.trainings import TrainingsService
from dependencies import (get_current_user, matches_service, players_service, trainings_service, get_conn)
from repositories.users import get_user_by_id

router = APIRouter()

@router.get("/", name="dashboard_ui")
async def dashboard_ui(
    request: Request,
    user: Optional[User] = Depends(get_current_user),
    matches_svc: MatchesService = Depends(matches_service),
    players_svc: PlayersService = Depends(players_service),
    trainings_svc: TrainingsService = Depends(trainings_service),
    conn: sqlite3.Connection = Depends(get_conn)
):

    template_user = user
    if user:
        full_user_data = get_user_by_id(conn, user.id)
        if full_user_data:
            template_user = full_user_data

    data = {}

    if user:
        # ADMIN
        if user.role == 'admin':

            all_matches = matches_svc.get_all_matches()
            all_players = players_svc.get_all_players()

            data = {
                "matches_count": len(all_matches),
                "players_count": len(all_players),
                "trainings_count": len(trainings_svc.get_all_trainings()),
                "recent_matches": all_matches[:3] #
            }

        # TRÉNER
        elif user.role == 'coach':

            matches = matches_svc.get_all_matches()
            trainings = trainings_svc.get_all_trainings()


            now_str = datetime.now().strftime("%Y-%m-%dT%H:%M")

            future_matches = [m for m in matches if m['date'] >= now_str]
            future_matches.sort(key=lambda x: x['date'])

            future_trainings = [t for t in trainings if t['date'] >= now_str]
            future_trainings.sort(key=lambda x: x['date'])

            data = {
                "next_match": future_matches[0] if future_matches else None,
                "next_training": future_trainings[0] if future_trainings else None,
                "matches_count": len(matches),
                "players_count": len(players_svc.get_all_players())
            }

        # HRÁČ
        elif user.role == 'player':

            events = players_svc.get_events_for_player(user.id)

            now_str = datetime.now().strftime("%Y-%m-%dT%H:%M")

            future_events = [e for e in events if e['date'] >= now_str]
            future_events.sort(key=lambda x: x['date'])

            data = {
                "upcoming_events": future_events,
                "total_events": len(events)
            }

    return request.app.state.templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "user": user,
            "data": data
        }
    )