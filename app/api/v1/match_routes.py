from app.responses.response_builder import success_response
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.match import (
    MatchCreate,
    MatchUpdate,
    MatchScoreboardResponse,
    SetScoreResponse,
    FinalizeMatchRequest,
    MatchEventResponse,
)
from app.services.match_service import MatchService
from app.middleware.auth_middleware import verify_token, require_roles

router = APIRouter()
manage_match = require_roles("Admin")
score_match = require_roles("Admin", "Scorer")


def _scoreboard_payload(result: dict):
    match_response = MatchService.build_match_response(result["match"])
    return MatchScoreboardResponse(
        match=match_response,
        completed_sets=[
            SetScoreResponse.model_validate(s) for s in result["completed_sets"]
        ],
        player1_display_point=result["player1_display_point"],
        player2_display_point=result["player2_display_point"],
    )


@router.post("/match")
def create_match(
    payload: MatchCreate,
    current_user=Depends(manage_match),
    db: Session = Depends(get_db),
):
    result = MatchService.create_match(db, payload)
    return success_response(
        message="Match created successfully",
        data=MatchService.build_match_response(result)
    )


@router.get("/matches")
def get_matches(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status: str | None = None,
    is_complete: bool | None = None,
    current_user=Depends(verify_token),
    db: Session = Depends(get_db),
):
    matches, total = MatchService.get_all_matches(db, page, page_size, status, is_complete)
    return success_response(
        message="Matches fetched successfully",
        data={
            "items": [MatchService.build_match_response(m) for m in matches],
            "total": total,
            "page": page,
            "page_size": page_size,
        },
    )


@router.get("/match/{match_id}")
def get_match(
    match_id: int, current_user=Depends(verify_token), db: Session = Depends(get_db)
):
    match = MatchService.get_match_by_id(db, match_id)
    return success_response(
        message="Match fetched successfully",
        data=MatchService.build_match_response(match)
    )


@router.put("/match/{match_id}")
def update_match(
    match_id: int,
    payload: MatchUpdate,
    current_user=Depends(manage_match),
    db: Session = Depends(get_db),
):
    result = MatchService.update_match(db, match_id, payload)
    return success_response(
        message="Match updated successfully",
        data=MatchService.build_match_response(result)
    )


@router.delete("/match/{match_id}")
def delete_match(
    match_id: int, current_user=Depends(manage_match), db: Session = Depends(get_db)
):
    deleted_by = current_user.get("user_id")
    MatchService.delete_match(db, match_id, deleted_by)
    return success_response(message="Match deleted successfully")


@router.post("/match/{match_id}/restore")
def restore_match(
    match_id: int, current_user=Depends(manage_match), db: Session = Depends(get_db)
):
    result = MatchService.restore_match(db, match_id)
    return success_response(
        message="Match restored successfully",
        data=MatchService.build_match_response(result)
    )


# ---------- Live scoring ----------


@router.get("/match/{match_id}/scoreboard")
def get_scoreboard(
    match_id: int, current_user=Depends(verify_token), db: Session = Depends(get_db)
):
    result = MatchService.get_scoreboard(db, match_id)
    return success_response(
        message="Scoreboard fetched successfully",
        data=_scoreboard_payload(result)
    )


@router.get("/match/{match_id}/events")
def get_match_events(
    match_id: int,
    current_user=Depends(verify_token),
    db: Session = Depends(get_db),
):
    events = MatchService.get_match_events(
        db,
        match_id,
    )

    return success_response(
        message="Match events fetched successfully",
        data=[MatchEventResponse.model_validate(event) for event in events],
    )


@router.post(
    "/match/{match_id}/finalize",
)
def finalize_match(
    match_id: int,
    data: FinalizeMatchRequest,
    current_user=Depends(score_match),
    db: Session = Depends(get_db),
):
    result = MatchService.finalize_match(
        db=db,
        match_id=match_id,
        data=data,
    )

    return success_response(
        message="Match finalized successfully",
        data=_scoreboard_payload(result)
    )
