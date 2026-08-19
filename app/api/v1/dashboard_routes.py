from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.tournament import Tournament
from app.models.player import Player
from app.models.official import Official
from app.models.match import Match
from app.middleware.auth_middleware import require_roles


router = APIRouter()

dashboard_access = require_roles()


@router.get("/dashboard/summary")
def get_dashboard_summary(
        current_user=Depends(dashboard_access),
        db: Session = Depends(get_db),
):
    tournament_active = (
        db.query(Tournament)
        .filter(
            Tournament.is_deleted == False,
            Tournament.is_active == True,
            )
        .count()
    )

    tournament_inactive = (
        db.query(Tournament)
        .filter(
            Tournament.is_deleted == False,
            Tournament.is_active == False,
            )
        .count()
    )

    tournament_all = (
        db.query(Tournament)
        .filter(
            Tournament.is_deleted == False,
            )
        .count()
    )

    player_active = (
        db.query(Player)
        .filter(
            Player.is_deleted == False,
            Player.is_active == True,
            )
        .count()
    )

    player_inactive = (
        db.query(Player)
        .filter(
            Player.is_deleted == False,
            Player.is_active == False,
            )
        .count()
    )

    player_all = (
        db.query(Player)
        .filter(
            Player.is_deleted == False,
            )
        .count()
    )

    official_active = (
        db.query(Official)
        .filter(
            Official.is_deleted == False,
            Official.is_active == True,
            )
        .count()
    )

    official_inactive = (
        db.query(Official)
        .filter(
            Official.is_deleted == False,
            Official.is_active == False,
            )
        .count()
    )

    official_all = (
        db.query(Official)
        .filter(
            Official.is_deleted == False,
            )
        .count()
    )

    match_active = (
        db.query(Match)
        .filter(
            Match.is_deleted == False,
            Match.is_active == True,
            )
        .count()
    )

    match_inactive = (
        db.query(Match)
        .filter(
            Match.is_deleted == False,
            Match.is_active == False,
            )
        .count()
    )

    match_all = (
        db.query(Match)
        .filter(
            Match.is_deleted == False,
            )
        .count()
    )

    return {
        "message": "Dashboard summary fetched successfully",
        "logged_in_user": current_user,
        "data": {
            "tournament": {
                "active": tournament_active,
                "inactive": tournament_inactive,
                "all": tournament_all,
            },
            "player": {
                "active": player_active,
                "inactive": player_inactive,
                "all": player_all,
            },
            "official": {
                "active": official_active,
                "inactive": official_inactive,
                "all": official_all,
            },
            "match": {
                "active": match_active,
                "inactive": match_inactive,
                "all": match_all,
            },
        },
    }