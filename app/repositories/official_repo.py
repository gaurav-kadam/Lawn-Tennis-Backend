from sqlalchemy.orm import Session
from app.models.official import Official
from app.utils.soft_delete import SoftDeleteHelper
from app.exceptions.db_safety import safe_commit


class OfficialRepository:

    @staticmethod
    def count_officials(db: Session, is_active: bool | None = None):
        query = db.query(Official).filter(Official.is_deleted == False)
        if is_active is not None:
            query = query.filter(Official.is_active == is_active)
        return query.count()

    @staticmethod
    def create_official(db: Session, data: dict):
        official = Official(**data)
        db.add(official)
        return safe_commit(db, official, "create_official")

    @staticmethod
    def get_official_by_id(db: Session, official_id: int):
        return db.query(Official).filter(Official.id == official_id, Official.is_deleted == False).first()

    @staticmethod
    def get_all_officials(db: Session, page: int = 1, page_size: int = 10, is_active: bool | None = None):
        query = db.query(Official).filter(Official.is_deleted == False)
        if is_active is not None:
            query = query.filter(Official.is_active == is_active)
        total = query.count()
        officials = query.offset((page - 1) * page_size).limit(page_size).all()
        return officials, total

    @staticmethod
    def update_official(db: Session, existing: Official, update_data: dict):
        for key, value in update_data.items():
            setattr(existing, key, value)
        return safe_commit(db, existing, "update_official")

    @staticmethod
    def delete_official(db: Session, official: Official, deleted_by: int | None = None):
        return SoftDeleteHelper.soft_delete(db, official, deleted_by)

    @staticmethod
    def restore_official(db: Session, official_id: int):
        official = db.query(Official).filter(Official.id == official_id).first()
        if not official:
            return None
        return SoftDeleteHelper.restore(db, official)
