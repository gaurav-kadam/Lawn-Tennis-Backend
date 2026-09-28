from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.utils.logger import logger


class SoftDeleteHelper:
    @staticmethod
    def soft_delete(db: Session, record, deleted_by: int | None = None):
        from app.exceptions.custom_exceptions import DatabaseException
        try:
            record.is_deleted = True
            record.deleted_at = datetime.now(timezone.utc)
            record.deleted_by = deleted_by
            db.commit()
            db.refresh(record)
            return record
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error during soft_delete: {str(e)}", exc_info=True)
            raise DatabaseException()

    @staticmethod
    def restore(db: Session, record):
        from app.exceptions.custom_exceptions import DatabaseException
        try:
            record.is_deleted = False
            record.deleted_at = None
            record.deleted_by = None
            db.commit()
            db.refresh(record)
            return record
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error during restore: {str(e)}", exc_info=True)
            raise DatabaseException()
