from app.responses.response_builder import success_response
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.official import OfficialCreate, OfficialUpdate, OfficialResponse
from app.services.official_service import OfficialService
from app.middleware.auth_middleware import verify_token, require_roles

router = APIRouter()


@router.post("/official")
def create_official(
    payload: OfficialCreate,
    current_user=Depends(require_roles("Admin")),
    db: Session = Depends(get_db),
):
    result = OfficialService.create_official(db, payload)
    return success_response(
        message="Official created successfully",
        data=OfficialResponse.model_validate(result),
    )


@router.get("/officials")
def get_officials(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    is_active: bool | None = None,
    current_user=Depends(verify_token),
    db: Session = Depends(get_db),
):
    officials, total = OfficialService.get_all_officials(db, page, page_size, is_active)
    return success_response(
        message="Officials fetched successfully",
        data={
            "items": [OfficialResponse.model_validate(o) for o in officials],
            "total": total,
            "page": page,
            "page_size": page_size,
        },
    )


@router.get("/official/{official_id}")
def get_official(
    official_id: int, current_user=Depends(verify_token), db: Session = Depends(get_db)
):
    official = OfficialService.get_official_by_id(db, official_id)
    return success_response(
        message="Official fetched successfully",
        data=OfficialResponse.model_validate(official),
    )


@router.put("/official/{official_id}")
def update_official(
    official_id: int,
    payload: OfficialUpdate,
    current_user=Depends(require_roles("Admin")),
    db: Session = Depends(get_db),
):
    result = OfficialService.update_official(db, official_id, payload)
    return success_response(
        message="Official updated successfully",
        data=OfficialResponse.model_validate(result),
    )


@router.delete("/official/{official_id}")
def delete_official(
    official_id: int,
    current_user=Depends(require_roles("Admin")),
    db: Session = Depends(get_db),
):
    deleted_by = current_user.get("user_id")
    OfficialService.delete_official(db, official_id, deleted_by)
    return success_response(message="Official deleted successfully")


@router.post("/official/{official_id}/restore")
def restore_official(
    official_id: int,
    current_user=Depends(require_roles("Admin")),
    db: Session = Depends(get_db),
):
    result = OfficialService.restore_official(db, official_id)
    return success_response(
        message="Official restored successfully",
        data=OfficialResponse.model_validate(result),
    )
