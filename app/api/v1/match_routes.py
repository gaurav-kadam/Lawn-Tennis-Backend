from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.match import (
    MatchCreate, MatchUpdate, MatchResponse, PointCreate,
    MatchScoreboardResponse, SetScoreResponse,
)
from app.schemas.log import PointLogResponse
from app.services.match_service import MatchService
from app.middleware.auth_middleware import verify_token, require_roles

router = APIRouter()

# Match metadata (create/edit/delete a match record) is an Admin action.
# Recording points/undo during a live match is done by the Scorer (and Admin).
# Everyone logged in (Admin/Scorer/Supervisor) can read match data and the scoreboard.
manage_match = require_roles("Admin")
score_match = require_roles("Admin", "Scorer")


def _scoreboard_payload(result: dict):
    return MatchScoreboardResponse(
        match=MatchResponse.model_validate(result["match"]),
        completed_sets=[SetScoreResponse.model_validate(s) for s in result["completed_sets"]],
        player1_display_point=result["player1_display_point"],
        player2_display_point=result["player2_display_point"],
    )


@router.post("/matches")
def create_match(payload: MatchCreate, current_user=Depends(manage_match), db: Session = Depends(get_db)):
    result = MatchService.create_match(db, payload)
    return {"message": "Match created successfully", "data": MatchResponse.model_validate(result)}


@router.get("/matches")
def get_matches(
        page: int = Query(1, ge=1),
        page_size: int = Query(10, ge=1, le=100),
        status: str | None = None,
        current_user=Depends(verify_token),
        db: Session = Depends(get_db),
):
    matches, total = MatchService.get_all_matches(db, page, page_size, status)
    return {
        "message": "Matches fetched successfully",
        "data": {
            "items": [MatchResponse.model_validate(m) for m in matches],
            "total": total,
            "page": page,
            "page_size": page_size,
        },
    }


@router.get("/matches/{match_id}")
def get_match(match_id: int, current_user=Depends(verify_token), db: Session = Depends(get_db)):
    match = MatchService.get_match_by_id(db, match_id)
    return {"message": "Match fetched successfully", "data": MatchResponse.model_validate(match)}


@router.put("/matches/{match_id}")
def update_match(match_id: int, payload: MatchUpdate, current_user=Depends(manage_match), db: Session = Depends(get_db)):
    result = MatchService.update_match(db, match_id, payload)
    return {"message": "Match updated successfully", "data": MatchResponse.model_validate(result)}


@router.delete("/matches/{match_id}")
def delete_match(match_id: int, current_user=Depends(manage_match), db: Session = Depends(get_db)):
    deleted_by = current_user.get("user_id")
    MatchService.delete_match(db, match_id, deleted_by)
    return {"message": "Match deleted successfully"}


@router.post("/matches/{match_id}/restore")
def restore_match(match_id: int, current_user=Depends(manage_match), db: Session = Depends(get_db)):
    result = MatchService.restore_match(db, match_id)
    return {"message": "Match restored successfully", "data": MatchResponse.model_validate(result)}


# ---------- Live scoring ----------

@router.get("/matches/{match_id}/scoreboard")
def get_scoreboard(match_id: int, current_user=Depends(verify_token), db: Session = Depends(get_db)):
    result = MatchService.get_scoreboard(db, match_id)
    return {"message": "Scoreboard fetched successfully", "data": _scoreboard_payload(result)}


@router.post("/matches/{match_id}/points")
def add_point(match_id: int, payload: PointCreate, current_user=Depends(score_match), db: Session = Depends(get_db)):
    result = MatchService.add_point(db, match_id, payload)
    return {"message": "Point recorded successfully", "data": _scoreboard_payload(result)}


@router.post("/matches/{match_id}/undo")
def undo_point(match_id: int, current_user=Depends(score_match), db: Session = Depends(get_db)):
    result = MatchService.undo_last_point(db, match_id)
    return {"message": "Last point undone successfully", "data": _scoreboard_payload(result)}


@router.get("/matches/{match_id}/logs")
def get_logs(match_id: int, current_user=Depends(verify_token), db: Session = Depends(get_db)):
    logs = MatchService.get_point_logs(db, match_id)
    return {"message": "Point logs fetched successfully", "data": [PointLogResponse.model_validate(l) for l in logs]}
