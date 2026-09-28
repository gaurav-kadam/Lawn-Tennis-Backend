from app.responses.response_builder import success_response
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.tournament import (
    TournamentCreate,
    TournamentUpdate,
    TournamentResponse,
)
from app.services.tournament_service import TournamentService
from app.middleware.auth_middleware import verify_token, require_roles

router = APIRouter()


@router.post("/tournament")
def create_tournament(
    payload: TournamentCreate,
    current_user=Depends(require_roles("Admin")),
    db: Session = Depends(get_db),
):
    result = TournamentService.create_tournament(db, payload)
    return success_response(
        message="Tournament created successfully",
        data=TournamentResponse.model_validate(result),
    )


@router.get("/tournaments")
def get_tournaments(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    is_active: bool | None = None,
    current_user=Depends(verify_token),
    db: Session = Depends(get_db),
):
    tournaments, total = TournamentService.get_all_tournaments(
        db, page, page_size, is_active
    )
    return success_response(
        message="Tournaments fetched successfully",
        data={
            "items": [TournamentResponse.model_validate(t) for t in tournaments],
            "total": total,
            "page": page,
            "page_size": page_size,
        },
    )


@router.get("/tournament/{tournament_id}")
def get_tournament(
    tournament_id: int,
    current_user=Depends(verify_token),
    db: Session = Depends(get_db),
):
    tournament = TournamentService.get_tournament_by_id(db, tournament_id)
    return success_response(
        message="Tournament fetched successfully",
        data=TournamentResponse.model_validate(tournament),
    )


@router.put("/tournament/{tournament_id}")
def update_tournament(
    tournament_id: int,
    payload: TournamentUpdate,
    current_user=Depends(require_roles("Admin")),
    db: Session = Depends(get_db),
):
    result = TournamentService.update_tournament(db, tournament_id, payload)
    return success_response(
        message="Tournament updated successfully",
        data=TournamentResponse.model_validate(result),
    )


@router.delete("/tournament/{tournament_id}")
def delete_tournament(
    tournament_id: int,
    current_user=Depends(require_roles("Admin")),
    db: Session = Depends(get_db),
):
    deleted_by = current_user.get("user_id")
    TournamentService.delete_tournament(db, tournament_id, deleted_by)
    return success_response(message="Tournament deleted successfully")


@router.post("/tournament/{tournament_id}/restore")
def restore_tournament(
    tournament_id: int,
    current_user=Depends(require_roles("Admin")),
    db: Session = Depends(get_db),
):
    result = TournamentService.restore_tournament(db, tournament_id)
    return success_response(
        message="Tournament restored successfully",
        data=TournamentResponse.model_validate(result),
    )
