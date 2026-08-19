from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import (
    auth_routes,
    base_routes,
    tournament_routes,
    official_routes,
    player_routes,
    match_routes,
    dashboard_routes,
)

from app.core.config import settings
from app.db.base import Base

from app.models import User
from app.models.role import Role
from app.models.tournament import Tournament
from app.models.player import Player
from app.models.official import Official
from app.models.match import Match, MatchSet, MatchPointLog

from app.db.session import engine, SessionLocal
from app.seeds.role_Seed import seed_roles
from app.exceptions import register_exception_handlers

_docs_enabled = settings.ENV != "production"

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs" if _docs_enabled else None,
    redoc_url="/redoc" if _docs_enabled else None,
    openapi_url="/openapi.json" if _docs_enabled else None,
)

register_exception_handlers(app)

db = SessionLocal()
try:
    seed_roles(db)
finally:
    db.close()

origins = [
    "http://localhost:8081",
    "http://127.0.0.1:8081",
    "http://localhost:3000",
    "http://localhost:4200",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router, prefix="/api/v1", tags=["Authentication"])
app.include_router(base_routes.router, prefix="/api/v1", tags=["Users"])
app.include_router(tournament_routes.router, prefix="/api/v1", tags=["Tournaments"])
app.include_router(player_routes.router, prefix="/api/v1", tags=["Players"])
app.include_router(official_routes.router, prefix="/api/v1", tags=["Officials"])
app.include_router(match_routes.router, prefix="/api/v1", tags=["Matches"])
app.include_router(dashboard_routes.router,prefix="/api/v1",tags=["Dashboard"])


@app.get("/")
def root():
    return {"message": "Tennis backend is running"}