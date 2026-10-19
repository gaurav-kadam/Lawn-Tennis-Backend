from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.middleware.auth_middleware import require_roles
from app.services.dashboard_service import (
    get_dashboard_summary as build_dashboard_summary,
)
from app.responses.response_builder import success_response


router = APIRouter()

dashboard_access = require_roles()


@router.get("/dashboard/summary")
def get_dashboard_summary(
        current_user=Depends(dashboard_access),
        db: Session = Depends(get_db),
):
    data = build_dashboard_summary(db)

    if isinstance(data, dict):
        response_data = {
            **data,
            "logged_in_user": current_user,
        }
    else:
        response_data = {
            "summary": data,
            "logged_in_user": current_user,
        }

    return success_response(
        message="Dashboard summary fetched successfully",
        data=response_data,
    )