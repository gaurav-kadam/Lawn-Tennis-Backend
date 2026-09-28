import time

from sqlalchemy.orm import Session

from app.exceptions import NotFoundException
from app.repositories.team_repo import TeamRepository
from app.schemas.team import TeamCreate, TeamUpdate


class TeamService:

    @staticmethod
    def _build_code(team_name: str) -> str:
        name_part = (
                "".join(ch for ch in team_name.upper() if ch.isalnum())[:10] or "TEAM"
        )

        return f"{name_part}_{int(time.time() * 1000)}"

    @staticmethod
    def create_team(db: Session, data: TeamCreate):
        payload = data.model_dump()

        payload["team_code"] = TeamService._build_code(data.team_name)
        payload["is_active"] = True

        return TeamRepository.create_team(db, payload)

    @staticmethod
    def get_team_by_id(db: Session, team_id: int):
        team = TeamRepository.get_team_by_id(db, team_id)

        if not team:
            raise NotFoundException("Team not found")

        return team

    @staticmethod
    def get_all_teams(
            db: Session,
            page: int,
            page_size: int,
            is_active: bool | None,
    ):
        return TeamRepository.get_all_teams(db, page, page_size, is_active)

    @staticmethod
    def update_team(db: Session, team_id: int, data: TeamUpdate):
        existing = TeamService.get_team_by_id(db, team_id)
        update_data = data.model_dump(exclude_unset=True)

        return TeamRepository.update_team(db, existing, update_data)

    @staticmethod
    def delete_team(
            db: Session, team_id: int, deleted_by: int | None = None
    ):
        existing = TeamService.get_team_by_id(db, team_id)
        TeamRepository.delete_team(db, existing, deleted_by)

        return True

    @staticmethod
    def restore_team(db: Session, team_id: int):
        result = TeamRepository.restore_team(db, team_id)

        if result is None:
            raise NotFoundException("Team not found")

        return result