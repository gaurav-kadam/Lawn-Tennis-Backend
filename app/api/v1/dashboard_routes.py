from app.responses.response_builder import success_response
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.middleware.auth_middleware import require_roles
from app.services.dashboard_service import get_dashboard_summary as build_dashboard_summary

router = APIRouter()

dashboard_access = require_roles()


@router.get("/dashboard/summary")
def get_dashboard_summary(
    current_user=Depends(dashboard_access),
    db: Session = Depends(get_db),
):
    data = build_dashboard_summary(db)
    response = success_response(
        message="Dashboard summary fetched successfully",
        data=data,
    ).model_dump()
    response["logged_in_user"] = current_user
    return response
