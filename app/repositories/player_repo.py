from sqlalchemy.orm import Session
from app.models.player import Player
from app.utils.soft_delete import SoftDeleteHelper
from app.exceptions.db_safety import safe_commit


class PlayerRepository:

    @staticmethod
    def count_players(db: Session, is_active: bool | None = None):
        query = db.query(Player).filter(Player.is_deleted == False)
        if is_active is not None:
            query = query.filter(Player.is_active == is_active)
        return query.count()

    @staticmethod
    def create_player(db: Session, data: dict):
        player = Player(**data)
        db.add(player)
        return safe_commit(db, player, "create_player")

    @staticmethod
    def get_player_by_id(db: Session, player_id: int):
        return db.query(Player).filter(Player.id == player_id, Player.is_deleted == False).first()

    @staticmethod
    def get_all_players(db: Session, page: int = 1, page_size: int = 10, is_active: bool | None = None):
        query = db.query(Player).filter(Player.is_deleted == False)
        if is_active is not None:
            query = query.filter(Player.is_active == is_active)
        total = query.count()
        players = query.offset((page - 1) * page_size).limit(page_size).all()
        return players, total

    @staticmethod
    def update_player(db: Session, existing: Player, update_data: dict):
        for key, value in update_data.items():
            setattr(existing, key, value)
        return safe_commit(db, existing, "update_player")

    @staticmethod
    def delete_player(db: Session, player: Player, deleted_by: int | None = None):
        return SoftDeleteHelper.soft_delete(db, player, deleted_by)

    @staticmethod
    def restore_player(db: Session, player_id: int):
        player = db.query(Player).filter(Player.id == player_id).first()
        if not player:
            return None
        return SoftDeleteHelper.restore(db, player)
