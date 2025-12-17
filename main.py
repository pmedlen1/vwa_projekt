# app/main.py
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
# from pages.items import router as items_router  # ← DŮLEŽITÉ: přímý import modulu
from pages.matches import router as match_router
from pages.dashboard import router as dashboard_router  # ← DŮLEŽITÉ: přímý import modulu
from pages.auth import router as auth_router
from dependencies import auth_service, get_current_user, matches_service, players_service, trainings_service
from services.items import ItemsService
from services.auth import AuthService
from services.matches import MatchesService
from pages.players import router as players_router
from services.players import PlayersService
from pages.trainings import router as trainings_router
from services.trainings import TrainingsService
from pages.profile import router as profile_router


def create_app() -> FastAPI:
    app = FastAPI(title="Futbalový Manažer", version="1.0.0")

    app.mount("/static", StaticFiles(directory="static"), name="static")
    app.state.templates = Jinja2Templates(directory="templates")

    app.include_router(dashboard_router, prefix="", tags=["homepage"])
    app.include_router(match_router, prefix="/matches", tags=["mathces"])
    app.include_router(auth_router, prefix="", tags=["auth"])
    app.include_router(players_router, prefix="/players", tags=["players"])
    app.include_router(trainings_router, prefix="/trainings", tags=["trainings"])
    app.include_router(profile_router, prefix="/profile", tags=["profile"])

    # DEBUG: vypiš zaregistrované cesty
    print("=== ROUTES ===")
    for r in app.routes:
        try:
            print(getattr(r, "methods", ""), getattr(r, "path", ""))
        except Exception:
            pass

    # Pokud používáš override přes třídu, nech, jinak ho klidně vyhoď
    app.dependency_overrides[MatchesService] = matches_service
    app.dependency_overrides[AuthService] = auth_service
    app.dependency_overrides[PlayersService] = players_service
    app.dependency_overrides[TrainingsService] = trainings_service


    app.add_middleware(SessionMiddleware, secret_key="dev-secret")

    app.state.templates.env.globals.update(get_user=lambda request: getattr(request.state, "user", None))

    @app.middleware("http")
    async def inject_user(request: Request, call_next):
        request.state.user = get_current_user(request)
        response = await call_next(request)
        return response

    return app

app = create_app()
