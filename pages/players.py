from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from starlette import status
from services.players import PlayersService
from services.auth import User
from dependencies import get_conn, get_current_user, require_admin_or_coach, players_service

router = APIRouter()

