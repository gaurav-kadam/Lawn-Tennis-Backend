from contextlib import contextmanager

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.exceptions.custom_exceptions import DatabaseException
from app.utils.logger import logger


def safe_commit(db: Session, obj, action: str, commit: bool = True):
    try:
        if commit:
            db.commit()
            db.refresh(obj)
        else:
            db.flush()
        return obj
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error during {action}: {str(e)}", exc_info=True)
        raise DatabaseException()


def safe_delete(db: Session, obj, action: str, commit: bool = True):
    try:
        db.delete(obj)
        if commit:
            db.commit()
        else:
            db.flush()
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error during {action}: {str(e)}", exc_info=True)
        raise DatabaseException()


def safe_query_delete(db: Session, query, action: str, commit: bool = True):
    try:
        query.delete()
        if commit:
            db.commit()
        else:
            db.flush()
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error during {action}: {str(e)}", exc_info=True)
        raise DatabaseException()


@contextmanager
def transaction(db: Session, action: str):
    try:
        yield db
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error during {action}: {str(e)}", exc_info=True)
        raise DatabaseException()
    except Exception:
        db.rollback()
        raise
