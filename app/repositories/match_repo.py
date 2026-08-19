from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.models.match import Match, MatchSet, MatchPointLog
from app.utils.soft_delete import SoftDeleteHelper
from app.exceptions.db_safety import safe_commit, safe_query_delete
from app.exceptions.custom_exceptions import DatabaseException
from app.utils.logger import logger


class MatchRepository:

    @staticmethod
    def create_match(db: Session, data: dict):
        match = Match(**data)
        db.add(match)
        return safe_commit(db, match, "create_match")

    @staticmethod
    def get_match_by_id(db: Session, match_id: int):
        return db.query(Match).filter(
            Match.id == match_id,
            Match.is_deleted == False
        ).first()

    @staticmethod
    def get_all_matches(
            db: Session,
            page: int = 1,
            page_size: int = 10,
            status: str | None = None
    ):
        query = db.query(Match).filter(
            Match.is_deleted == False
        )

        if status:
            query = query.filter(Match.status == status)

        total = query.count()

        matches = (
            query.order_by(Match.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        return matches, total

    @staticmethod
    def update_match(
            db: Session,
            existing: Match,
            update_data: dict,
            commit: bool = True
    ):
        for key, value in update_data.items():
            setattr(existing, key, value)

        return safe_commit(
            db,
            existing,
            "update_match",
            commit=commit
        )

    @staticmethod
    def delete_match(
            db: Session,
            match: Match,
            deleted_by: int | None = None
    ):
        return SoftDeleteHelper.soft_delete(
            db,
            match,
            deleted_by
        )

    @staticmethod
    def restore_match(db: Session, match_id: int):
        match = db.query(Match).filter(
            Match.id == match_id
        ).first()

        if not match:
            return None

        return SoftDeleteHelper.restore(db, match)

    @staticmethod
    def get_point_logs(db: Session, match_id: int):
        return (
            db.query(MatchPointLog)
            .filter(MatchPointLog.match_id == match_id)
            .order_by(MatchPointLog.point_number)
            .all()
        )

    @staticmethod
    def add_point_log(
            db: Session,
            data: dict,
            commit: bool = True
    ):
        log = MatchPointLog(
            **data,
            created_at=datetime.now(timezone.utc)
        )

        db.add(log)

        return safe_commit(
            db,
            log,
            "add_point_log",
            commit=commit
        )

    @staticmethod
    def delete_last_point_log(
            db: Session,
            match_id: int,
            commit: bool = True
    ):
        last = (
            db.query(MatchPointLog)
            .filter(MatchPointLog.match_id == match_id)
            .order_by(MatchPointLog.point_number.desc())
            .first()
        )

        if not last:
            return None

        try:
            db.delete(last)

            if commit:
                db.commit()
            else:
                db.flush()

        except SQLAlchemyError as e:
            db.rollback()
            logger.error(
                f"Database error: {str(e)}",
                exc_info=True
            )
            raise DatabaseException()

        return last

    @staticmethod
    def get_match_sets(db: Session, match_id: int):
        return (
            db.query(MatchSet)
            .filter(MatchSet.match_id == match_id)
            .order_by(MatchSet.set_number)
            .all()
        )

    @staticmethod
    def add_match_set(
            db: Session,
            data: dict,
            commit: bool = True
    ):
        match_set = MatchSet(**data)
        db.add(match_set)

        return safe_commit(
            db,
            match_set,
            "add_match_set",
            commit=commit
        )

    @staticmethod
    def delete_match_sets_after(
            db: Session,
            match_id: int,
            keep_count: int,
            commit: bool = True
    ):
        query = db.query(MatchSet).filter(
            MatchSet.match_id == match_id,
            MatchSet.set_number > keep_count
        )

        return safe_query_delete(
            db,
            query,
            "delete_match_sets_after",
            commit=commit
        )