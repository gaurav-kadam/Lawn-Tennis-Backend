from sqlalchemy.orm import Session
from app.models.tournament import Tournament
from app.utils.soft_delete import SoftDeleteHelper
from app.exceptions.db_safety import safe_commit


class TournamentRepository:

    @staticmethod
    def create_tournament(db: Session, data: dict):
        tournament = Tournament(**data)
        db.add(tournament)
        return safe_commit(db, tournament, "create_tournament")

    @staticmethod
    def get_tournament_by_id(db: Session, tournament_id: int):
        return db.query(Tournament).filter(
            Tournament.id == tournament_id, Tournament.is_deleted == False
        ).first()

    @staticmethod
    def get_all_tournaments(db: Session, page: int = 1, page_size: int = 10, is_active: bool | None = None):
        query = db.query(Tournament).filter(Tournament.is_deleted == False)
        if is_active is not None:
            query = query.filter(Tournament.is_active == is_active)
        total = query.count()
        tournaments = query.offset((page - 1) * page_size).limit(page_size).all()
        return tournaments, total

    @staticmethod
    def update_tournament(db: Session, existing_tournament: Tournament, update_data: dict):
        for key, value in update_data.items():
            setattr(existing_tournament, key, value)
        return safe_commit(db, existing_tournament, "update_tournament")

    @staticmethod
    def delete_tournament(db: Session, tournament: Tournament, deleted_by: int | None = None):
        return SoftDeleteHelper.soft_delete(db, tournament, deleted_by)

    @staticmethod
    def restore_tournament(db: Session, tournament_id: int):
        tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
        if not tournament:
            return None
        return SoftDeleteHelper.restore(db, tournament)

    @staticmethod
    def get_tournament_by_code(db: Session, tournament_code: str):
        return db.query(Tournament).filter(
            Tournament.tournament_code == tournament_code, Tournament.is_deleted == False
        ).first()
