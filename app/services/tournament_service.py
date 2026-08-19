from sqlalchemy.orm import Session
from app.exceptions import NotFoundException, ConflictException, BadRequestException, AuthenticationException
import time

from app.repositories.tournament_repo import TournamentRepository
from app.schemas.tournament import TournamentCreate, TournamentUpdate
from app.utils.logger import logger


class TournamentService:

    @staticmethod
    def _build_code(name: str) -> str:
        name_part = "".join(ch for ch in name.upper() if ch.isalnum())[:12] or "TOURNAMENT"
        return f"{name_part}_{int(time.time() * 1000)}"

    @staticmethod
    def create_tournament(db: Session, data: TournamentCreate):
        payload = data.model_dump()
        payload["tournament_code"] = TournamentService._build_code(data.tournament_name)
        payload["is_active"] = True
        logger.info(f"Creating tournament: {payload['tournament_name']}")
        return TournamentRepository.create_tournament(db, payload)

    @staticmethod
    def get_tournament_by_id(db: Session, tournament_id: int):
        tournament = TournamentRepository.get_tournament_by_id(db, tournament_id)
        if not tournament:
            raise NotFoundException("Tournament not found")
        return tournament

    @staticmethod
    def get_all_tournaments(db: Session, page: int, page_size: int, is_active: bool | None):
        tournaments, total = TournamentRepository.get_all_tournaments(db, page, page_size, is_active)
        return tournaments, total

    @staticmethod
    def update_tournament(db: Session, tournament_id: int, data: TournamentUpdate):
        existing = TournamentService.get_tournament_by_id(db, tournament_id)
        update_data = data.model_dump(exclude_unset=True)
        return TournamentRepository.update_tournament(db, existing, update_data)

    @staticmethod
    def delete_tournament(db: Session, tournament_id: int, deleted_by: int | None = None):
        existing = TournamentService.get_tournament_by_id(db, tournament_id)
        TournamentRepository.delete_tournament(db, existing, deleted_by)
        return True

    @staticmethod
    def restore_tournament(db: Session, tournament_id: int):
        result = TournamentRepository.restore_tournament(db, tournament_id)
        if result is None:
            raise NotFoundException("Tournament not found")
        return result
