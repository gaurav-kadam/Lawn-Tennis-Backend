from fastapi import (
    APIRouter,
    Depends,
    Query,
)

from sqlalchemy.orm import Session

from app.db.session import get_db

from app.schemas.team import (
    TeamCreate,
    TeamUpdate,
    TeamResponse,
)

from app.services.team_service import (
    TeamService,
)

from app.middleware.auth_middleware import (
    verify_token,
    require_roles,
)


router = APIRouter()


@router.post("/teams")
def create_team(
        payload: TeamCreate,
        current_user=Depends(
            require_roles("Admin")
        ),
        db: Session = Depends(get_db),
):

    result = TeamService.create_team(
        db,
        payload,
    )

    return {
        "message": "Team created successfully",
        "data": TeamResponse.model_validate(
            result
        ),
    }


@router.get("/teams")
def get_teams(
        page: int = Query(
            1,
            ge=1,
        ),
        page_size: int = Query(
            10,
            ge=1,
            le=100,
        ),
        is_active: bool | None = None,

        current_user=Depends(
            verify_token
        ),

        db: Session = Depends(
            get_db
        ),
):

    teams, total = (
        TeamService.get_all_teams(
            db,
            page,
            page_size,
            is_active,
        )
    )

    return {
        "message": "Teams fetched successfully",
        "data": {
            "items": [
                TeamResponse.model_validate(
                    team
                )
                for team in teams
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
        },
    }


@router.get("/teams/{team_id}")
def get_team(
        team_id: int,

        current_user=Depends(
            verify_token
        ),

        db: Session = Depends(
            get_db
        ),
):

    team = TeamService.get_team_by_id(
        db,
        team_id,
    )

    return {
        "message": "Team fetched successfully",

        "data": TeamResponse.model_validate(
            team
        ),
    }


@router.put("/teams/{team_id}")
def update_team(
        team_id: int,

        payload: TeamUpdate,

        current_user=Depends(
            require_roles("Admin")
        ),

        db: Session = Depends(
            get_db
        ),
):

    result = TeamService.update_team(
        db,
        team_id,
        payload,
    )

    return {
        "message": "Team updated successfully",

        "data": TeamResponse.model_validate(
            result
        ),
    }


@router.delete("/teams/{team_id}")
def delete_team(
        team_id: int,

        current_user=Depends(
            require_roles("Admin")
        ),

        db: Session = Depends(
            get_db
        ),
):

    deleted_by = current_user.get(
        "user_id"
    )

    TeamService.delete_team(
        db,
        team_id,
        deleted_by,
    )

    return {
        "message": "Team deleted successfully"
    }


@router.post("/teams/{team_id}/restore")
def restore_team(
        team_id: int,

        current_user=Depends(
            require_roles("Admin")
        ),
        db: Session = Depends(
            get_db
        ),
):

    result = TeamService.restore_team(
        db,
        team_id,
    )

    return {
        "message": "Team restored successfully",

        "data": TeamResponse.model_validate(
            result
        ),
    }