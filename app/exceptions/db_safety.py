"""
Reusable, safe database helpers used by every repository.

The contract for the whole app: a repository NEVER lets a raw SQLAlchemyError
escape. It always rolls back the session, logs the real error (table/column/
constraint details, full stack trace), and raises DatabaseException - a plain,
safe, generic message - which the global handler in app.exceptions.handlers
turns into a clean response. The client never sees SQL, table names, or
internal details.
"""

from contextlib import contextmanager

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.exceptions.custom_exceptions import DatabaseException
from app.utils.logger import logger


def safe_commit(db: Session, obj, action: str, commit: bool = True):
    """
    Stage + persist a single object.

    commit=True  (default): commit immediately, refresh, return the object.
                  Correct for simple, single-write CRUD (tournaments, players,
                  officials, single-record updates).
    commit=False: only flush (assigns PKs / runs constraint checks without
                  ending the transaction) so several of these can be combined
                  into one atomic commit via the `transaction()` context
                  manager below - needed when several related records must be
                  persisted atomically so they all succeed or all fail
                  together.
    """
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
    """For bulk .delete() on a query (not a single mapped object)."""
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
