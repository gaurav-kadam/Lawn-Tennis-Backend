from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.utils.logger import logger


class SoftDeleteHelper:
    """
    Used by every repository for delete/restore, so this is a shared choke
    point too - same rollback + DatabaseException contract as
    app.exceptions.db_safety (kept separate from that module only to avoid a
    circular import, since db_safety already depends on nothing here).
    """

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
