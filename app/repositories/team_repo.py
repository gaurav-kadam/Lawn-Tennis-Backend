from sqlalchemy.orm import Session

from app.models.team import Team
from app.utils.soft_delete import SoftDeleteHelper
from app.exceptions.db_safety import safe_commit


class TeamRepository:

    @staticmethod
    def create_team(db: Session, data: dict):
        team = Team(**data)

        db.add(team)

        return safe_commit(
            db,
            team,
            "create_team",
        )

    @staticmethod
    def get_team_by_id(
            db: Session,
            team_id: int,
    ):
        return (
            db.query(Team)
            .filter(
                Team.id == team_id,
                Team.is_deleted == False,
                )
            .first()
        )

    @staticmethod
    def get_all_teams(
            db: Session,
            page: int = 1,
            page_size: int = 10,
            is_active: bool | None = None,
    ):
        query = (
            db.query(Team)
            .filter(Team.is_deleted == False)
        )

        if is_active is not None:
            query = query.filter(
                Team.is_active == is_active
            )

        total = query.count()

        teams = (
            query
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        return teams, total

    @staticmethod
    def update_team(
            db: Session,
            existing: Team,
            update_data: dict,
    ):
        for key, value in update_data.items():
            setattr(existing, key, value)

        return safe_commit(
            db,
            existing,
            "update_team",
        )

    @staticmethod
    def delete_team(
            db: Session,
            team: Team,
            deleted_by: int | None = None,
    ):
        return SoftDeleteHelper.soft_delete(
            db,
            team,
            deleted_by,
        )
    @staticmethod
    def restore_team(
            db: Session,
            team_id: int,
    ):
        team = (
            db.query(Team)
            .filter(Team.id == team_id)
            .first()
        )
        if not team:
            return None
        return SoftDeleteHelper.restore(
            db,
            team,
        )