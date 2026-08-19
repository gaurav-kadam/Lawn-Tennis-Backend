from sqlalchemy.orm import Session
from app.exceptions import NotFoundException, ConflictException, BadRequestException, AuthenticationException
import time

from app.repositories.player_repo import PlayerRepository
from app.schemas.player import PlayerCreate, PlayerUpdate
from app.utils.logger import logger


class PlayerService:

    @staticmethod
    def _build_code(name: str) -> str:
        name_part = "".join(ch for ch in name.upper() if ch.isalnum())[:10] or "PLAYER"
        return f"{name_part}_{int(time.time() * 1000)}"

    @staticmethod
    def create_player(db: Session, data: PlayerCreate):
        payload = data.model_dump()
        payload["player_code"] = PlayerService._build_code(data.player_name)
        payload["is_active"] = True
        logger.info(f"Creating player: {payload['player_name']}")
        return PlayerRepository.create_player(db, payload)

    @staticmethod
    def get_player_by_id(db: Session, player_id: int):
        player = PlayerRepository.get_player_by_id(db, player_id)
        if not player:
            raise NotFoundException("Player not found")
        return player

    @staticmethod
    def get_all_players(db: Session, page: int, page_size: int, is_active: bool | None):
        return PlayerRepository.get_all_players(db, page, page_size, is_active)

    @staticmethod
    def update_player(db: Session, player_id: int, data: PlayerUpdate):
        existing = PlayerService.get_player_by_id(db, player_id)
        update_data = data.model_dump(exclude_unset=True)
        return PlayerRepository.update_player(db, existing, update_data)

    @staticmethod
    def delete_player(db: Session, player_id: int, deleted_by: int | None = None):
        existing = PlayerService.get_player_by_id(db, player_id)
        PlayerRepository.delete_player(db, existing, deleted_by)
        return True

    @staticmethod
    def restore_player(db: Session, player_id: int):
        result = PlayerRepository.restore_player(db, player_id)
        if result is None:
            raise NotFoundException("Player not found")
        return result
