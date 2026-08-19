from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.player import PlayerCreate, PlayerUpdate, PlayerResponse
from app.services.player_service import PlayerService
from app.middleware.auth_middleware import verify_token, require_roles

router = APIRouter()


@router.post("/players")
def create_player(payload: PlayerCreate, current_user=Depends(require_roles("Admin")), db: Session = Depends(get_db)):
    result = PlayerService.create_player(db, payload)
    return {"message": "Player created successfully", "data": PlayerResponse.model_validate(result)}


@router.get("/players")
def get_players(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    is_active: bool | None = None,
    current_user=Depends(verify_token),
    db: Session = Depends(get_db),
):
    players, total = PlayerService.get_all_players(db, page, page_size, is_active)
    return {
        "message": "Players fetched successfully",
        "data": {
            "items": [PlayerResponse.model_validate(p) for p in players],
            "total": total,
            "page": page,
            "page_size": page_size,
        },
    }


@router.get("/players/{player_id}")
def get_player(player_id: int, current_user=Depends(verify_token), db: Session = Depends(get_db)):
    player = PlayerService.get_player_by_id(db, player_id)
    return {"message": "Player fetched successfully", "data": PlayerResponse.model_validate(player)}


@router.put("/players/{player_id}")
def update_player(player_id: int, payload: PlayerUpdate, current_user=Depends(require_roles("Admin")), db: Session = Depends(get_db)):
    result = PlayerService.update_player(db, player_id, payload)
    return {"message": "Player updated successfully", "data": PlayerResponse.model_validate(result)}


@router.delete("/players/{player_id}")
def delete_player(player_id: int, current_user=Depends(require_roles("Admin")), db: Session = Depends(get_db)):
    deleted_by = current_user.get("user_id")
    PlayerService.delete_player(db, player_id, deleted_by)
    return {"message": "Player deleted successfully"}


@router.post("/players/{player_id}/restore")
def restore_player(player_id: int, current_user=Depends(require_roles("Admin")), db: Session = Depends(get_db)):
    result = PlayerService.restore_player(db, player_id)
    return {"message": "Player restored successfully", "data": PlayerResponse.model_validate(result)}
