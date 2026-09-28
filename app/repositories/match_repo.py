from sqlalchemy.orm import Session

from app.models.match import Match, MatchSet, MatchEvent
from app.utils.soft_delete import SoftDeleteHelper
from app.exceptions.db_safety import safe_commit, safe_query_delete


class MatchRepository:

    @staticmethod
    def count_matches(db: Session, is_active: bool | None = None):
        query = db.query(Match).filter(Match.is_deleted == False)
        if is_active is not None:
            query = query.filter(Match.is_active == is_active)
        return query.count()

    @staticmethod
    def create_match(db: Session, data: dict):
        match = Match(**data)
        db.add(match)
        return safe_commit(db, match, "create_match")

    @staticmethod
    def get_match_by_id(db: Session, match_id: int, for_update: bool = False):
        query = db.query(Match).filter(
            Match.id == match_id, Match.is_deleted == False
        )
        if for_update:
            query = query.populate_existing().with_for_update()
        return query.first()

    @staticmethod
    def get_all_matches(
            db: Session,
            page: int = 1,
            page_size: int = 10,
            status: str | None = None,
            is_complete: bool | None = None,
    ):
        query = db.query(Match).filter(Match.is_deleted == False)

        if status:
            query = query.filter(Match.status == status)

        if is_complete is True:
            query = query.filter(Match.status == "COMPLETED")
        elif is_complete is False:
            query = query.filter(Match.status != "COMPLETED")

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
            db: Session, existing: Match, update_data: dict, commit: bool = True
    ):
        for key, value in update_data.items():
            setattr(existing, key, value)

        return safe_commit(db, existing, "update_match", commit=commit)

    @staticmethod
    def delete_match(
            db: Session, match: Match, deleted_by: int | None = None
    ):
        return SoftDeleteHelper.soft_delete(db, match, deleted_by)

    @staticmethod
    def restore_match(db: Session, match_id: int):
        match = db.query(Match).filter(Match.id == match_id).first()

        if not match:
            return None

        return SoftDeleteHelper.restore(db, match)

    @staticmethod
    def get_match_sets(db: Session, match_id: int):
        return (
            db.query(MatchSet)
            .filter(MatchSet.match_id == match_id)
            .order_by(MatchSet.set_number)
            .all()
        )

    @staticmethod
    def add_match_set(db: Session, data: dict, commit: bool = True):
        match_set = MatchSet(**data)
        db.add(match_set)

        return safe_commit(db, match_set, "add_match_set", commit=commit)

    @staticmethod
    def delete_match_sets_after(
            db: Session, match_id: int, keep_count: int, commit: bool = True
    ):
        query = db.query(MatchSet).filter(
            MatchSet.match_id == match_id,
            MatchSet.set_number > keep_count,
            )

        return safe_query_delete(
            db, query, "delete_match_sets_after", commit=commit
        )

    @staticmethod
    def get_match_events(db: Session, match_id: int) -> list[MatchEvent]:
        return (
            db.query(MatchEvent)
            .filter(MatchEvent.match_id == match_id)
            .order_by(MatchEvent.event_number.asc())
            .all()
        )

    @staticmethod
    def create_match_events(
            db: Session, match_id: int, events: list[dict]
    ) -> list[MatchEvent]:
        if not events:
            return []

        db_events = [
            MatchEvent(
                match_id=match_id,
                event_number=event["event_number"],
                event_type=event["event_type"],
                player=event["player"],
                server=event.get("server"),
                elapsed_seconds=event.get("elapsed_seconds", 0),
                recorded_at=event.get("recorded_at"),
            )
            for event in events
        ]

        db.add_all(db_events)

        return db_events

    @staticmethod
    def delete_match_events(db: Session, match_id: int) -> None:
        (
            db.query(MatchEvent)
            .filter(MatchEvent.match_id == match_id)
            .delete(synchronize_session=False)
        )

    @staticmethod
    def has_match_events(db: Session, match_id: int) -> bool:
        return (
                db.query(MatchEvent.id)
                .filter(MatchEvent.match_id == match_id)
                .first()
                is not None
        )