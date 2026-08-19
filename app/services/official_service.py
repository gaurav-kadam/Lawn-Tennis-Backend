from sqlalchemy.orm import Session
from app.exceptions import NotFoundException, ConflictException, BadRequestException, AuthenticationException
import time

from app.repositories.official_repo import OfficialRepository
from app.schemas.official import OfficialCreate, OfficialUpdate
from app.utils.logger import logger


class OfficialService:

    @staticmethod
    def _build_code(name: str) -> str:
        name_part = "".join(ch for ch in name.upper() if ch.isalnum())[:10] or "OFFICIAL"
        return f"{name_part}_{int(time.time() * 1000)}"

    @staticmethod
    def create_official(db: Session, data: OfficialCreate):
        payload = data.model_dump()
        payload["official_code"] = OfficialService._build_code(data.official_name)
        payload["is_active"] = True
        logger.info(f"Creating official: {payload['official_name']}")
        return OfficialRepository.create_official(db, payload)

    @staticmethod
    def get_official_by_id(db: Session, official_id: int):
        official = OfficialRepository.get_official_by_id(db, official_id)
        if not official:
            raise NotFoundException("Official not found")
        return official

    @staticmethod
    def get_all_officials(db: Session, page: int, page_size: int, is_active: bool | None):
        return OfficialRepository.get_all_officials(db, page, page_size, is_active)

    @staticmethod
    def update_official(db: Session, official_id: int, data: OfficialUpdate):
        existing = OfficialService.get_official_by_id(db, official_id)
        update_data = data.model_dump(exclude_unset=True)
        return OfficialRepository.update_official(db, existing, update_data)

    @staticmethod
    def delete_official(db: Session, official_id: int, deleted_by: int | None = None):
        existing = OfficialService.get_official_by_id(db, official_id)
        OfficialRepository.delete_official(db, existing, deleted_by)
        return True

    @staticmethod
    def restore_official(db: Session, official_id: int):
        result = OfficialRepository.restore_official(db, official_id)
        if result is None:
            raise NotFoundException("Official not found")
        return result
