from datetime import datetime, timezone
from sqlalchemy import inspect
from sqlalchemy.orm import Session
from app.exceptions import (
    NotFoundException,
    ConflictException,
    BadRequestException,
    transaction,
)
from app.repositories.match_repo import MatchRepository
from app.schemas.match import MatchCreate, MatchUpdate, FinalizeMatchRequest, MatchResponse
from app.services.serving_state import (
    PLAYER1,
    PLAYER2,
    initialize_from_config,
    from_legacy,
    serving_state_to_dict,
    serving_state_from_dict,
)
from app.utils.logger import logger

VALID_FORMATS = {"BEST_OF_3", "BEST_OF_5"}


class MatchService:

    @staticmethod
    def build_match_response(match):
        serving_state = match.serving_state
        if serving_state is None:
            legacy_state = from_legacy(
                match.match_type,
                match.first_server,
                match.service_order,
            )
            serving_state = dict(serving_state_to_dict(legacy_state))

        match_data = {
            attribute.key: getattr(match, attribute.key)
            for attribute in inspect(match).mapper.column_attrs
        }
        match_data["serving_state"] = serving_state
        match_data["current_server"] = serving_state["current_server"]
        return MatchResponse.model_validate(match_data)

    @staticmethod
    def create_match(db: Session, data: MatchCreate):
        if data.match_format not in VALID_FORMATS:
            raise BadRequestException("match_format must be BEST_OF_3 or BEST_OF_5")

        payload = data.model_dump()

        if "round" in payload:
            payload["round_name"] = payload.pop("round")

        try:
            config = data.serving_state or {}
            configured_first = config.get("first_server") or data.first_server
            configured_opposing = config.get("opposing_first_server")
            serving = initialize_from_config(
                data.match_type,
                configured_first,
                configured_opposing,
                data.service_order,
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise BadRequestException(str(exc)) from exc

        payload["serving_state"] = dict(serving_state_to_dict(serving))

        if data.match_type == "DOUBLES":
            payload["service_order"] = list(serving.current_set_service_order)
            side = (
                PLAYER1 if serving.current_server in ("PLAYER1", "PLAYER2") else PLAYER2
            )
            payload["first_server"] = side
            payload["server"] = side
        else:
            payload["first_server"] = serving.first_server
            payload["server"] = serving.current_server

        payload["status"] = "LIVE"

        logger.info(
            f"Creating {data.match_type} match: "
            f"{data.player1_name} vs {data.player2_name}"
        )

        return MatchRepository.create_match(db, payload)

    @staticmethod
    def get_match_by_id(db: Session, match_id: int, for_update: bool = False):
        match = MatchRepository.get_match_by_id(db, match_id, for_update=for_update)
        if not match:
            raise NotFoundException("Match not found")
        return match

    @staticmethod
    def get_match_events(db: Session, match_id: int):
        MatchService.get_match_by_id(db, match_id)
        return MatchRepository.get_match_events(db, match_id)

    @staticmethod
    def get_all_matches(
        db: Session, page: int, page_size: int, status_filter: str | None,
        is_complete: bool | None = None,
    ):
        return MatchRepository.get_all_matches(db, page, page_size, status_filter, is_complete)

    @staticmethod
    def update_match(db: Session, match_id: int, data: MatchUpdate):
        match = MatchService.get_match_by_id(db, match_id)

        update_data = data.model_dump(exclude_unset=True)

        doubles_fields = {
            "player3_name",
            "player4_name",
            "service_order",
        }
        if match.match_type == "SINGLES":
            for field in doubles_fields:
                update_data.pop(field, None)
        elif match.match_type == "DOUBLES":
            service_order = update_data.get("service_order")
            if service_order:
                expected_players = {
                    "PLAYER1",
                    "PLAYER2",
                    "PLAYER3",
                    "PLAYER4",
                }
                if (
                    len(service_order) != 4
                    or len(set(service_order)) != 4
                    or set(service_order) != expected_players
                ):
                    raise BadRequestException(
                        "service_order must contain PLAYER1, PLAYER2, PLAYER3 and PLAYER4"
                    )

        if "serving_state" in update_data:
            if (
                match.player1_points
                or match.player2_points
                or match.player1_games
                or match.player2_games
                or match.player1_sets
                or match.player2_sets
                or match.is_tiebreak
                or MatchRepository.has_match_events(db, match.id)
            ):
                raise BadRequestException(
                    "serving_state cannot be changed after scoring has started"
                )
            try:
                raw_state = update_data["serving_state"] or {}
                serving = initialize_from_config(
                    match.match_type,
                    raw_state.get("first_server") or match.first_server,
                    raw_state.get("opposing_first_server"),
                    raw_state.get("current_set_service_order") or match.service_order,
                )
                update_data["serving_state"] = dict(serving_state_to_dict(serving))
                if match.match_type == "DOUBLES":
                    update_data["service_order"] = list(
                        serving.current_set_service_order
                    )
                    side = (
                        PLAYER1
                        if serving.current_server in ("PLAYER1", "PLAYER2")
                        else PLAYER2
                    )
                    update_data["first_server"] = side
                    update_data["server"] = side
                else:
                    update_data["first_server"] = serving.first_server
                    update_data["server"] = serving.current_server
            except (TypeError, ValueError) as exc:
                raise BadRequestException(str(exc)) from exc

        return MatchRepository.update_match(
            db,
            match,
            update_data,
        )

    @staticmethod
    def delete_match(db: Session, match_id: int, deleted_by: int | None = None):
        match = MatchService.get_match_by_id(db, match_id)
        MatchRepository.delete_match(db, match, deleted_by)
        return True

    @staticmethod
    def restore_match(db: Session, match_id: int):
        result = MatchRepository.restore_match(db, match_id)
        if not result:
            raise NotFoundException("Match not found")
        return result

    @staticmethod
    def get_scoreboard(
        db: Session,
        match_id: int,
    ):
        match = MatchService.get_match_by_id(
            db,
            match_id,
        )

        completed_sets = MatchRepository.get_match_sets(
            db,
            match_id,
        )

        state = {
            "is_tiebreak": match.is_tiebreak,
            "tiebreak_player1_points": match.tiebreak_player1_points,
            "tiebreak_player2_points": match.tiebreak_player2_points,
            "player1_points": match.player1_points,
            "player2_points": match.player2_points,
        }
        if state["is_tiebreak"]:
            p1_display = str(state["tiebreak_player1_points"])
            p2_display = str(state["tiebreak_player2_points"])
        else:
            p1 = state["player1_points"]
            p2 = state["player2_points"]
            names = {0: "0", 1: "15", 2: "30", 3: "40"}
            if p1 <= 3 and p2 <= 3:
                p1_display, p2_display = names[p1], names[p2]
            elif p1 == p2:
                p1_display, p2_display = "40", "40"
            elif p1 > p2:
                p1_display, p2_display = "AD", "40"
            else:
                p1_display, p2_display = "40", "AD"

        return {
            "match": match,
            "completed_sets": completed_sets,
            "player1_display_point": p1_display,
            "player2_display_point": p2_display,
        }

    @staticmethod
    def _validate_final_state(match, data):
        """Check references and structure, not tennis scoring correctness."""
        if match.match_type not in ("SINGLES", "DOUBLES"):
            raise BadRequestException("Invalid saved match type")
        if match.match_format not in VALID_FORMATS:
            raise BadRequestException("Invalid saved match format")
        slots = (
            ("PLAYER1", "PLAYER2")
            if match.match_type == "SINGLES"
            else ("PLAYER1", "PLAYER2", "PLAYER3", "PLAYER4")
        )
        for slot in slots:
            name = getattr(match, f"{slot.lower()}_name", None)
            if not name or not name.strip():
                raise BadRequestException("Match player configuration is incomplete")
        for event in data.events:
            if event.player not in slots or (
                event.server is not None and event.server not in slots
            ):
                raise BadRequestException(
                    "Event player/server is not valid for this match"
                )
        state = data.final_state
        max_sets = 3 if match.match_format == "BEST_OF_3" else 5
        if not 1 <= len(state.completed_sets) <= max_sets:
            raise BadRequestException(
                "Completed set count is incompatible with match format"
            )
        if state.player1_sets + state.player2_sets != len(state.completed_sets):
            raise BadRequestException("Set totals must match the completed set count")
        snapshots = [state.serving_state]
        for completed in state.completed_sets:
            if (completed.tiebreak_player1_points is None) != (
                completed.tiebreak_player2_points is None
            ):
                raise BadRequestException(
                    "Set tiebreak values must be supplied together"
                )
            snapshots.append(completed.serving_state)
        for snapshot in snapshots:
            if snapshot is None:
                continue
            if snapshot.get("match_type", match.match_type) != match.match_type:
                raise BadRequestException(
                    "Serving-state match type does not match the match"
                )
            try:
                serving_state_from_dict({"match_type": match.match_type, **snapshot})
            except (TypeError, ValueError) as exc:
                raise BadRequestException(str(exc)) from exc

    @staticmethod
    def finalize_match(
        db: Session,
        match_id: int,
        data: FinalizeMatchRequest,
    ):
        events = sorted(data.events, key=lambda event: event.event_number)
        if [event.event_number for event in events] != list(range(1, len(events) + 1)):
            raise BadRequestException("event_number must start at 1 and be continuous")
        if data.final_state.match_winner is None:
            raise BadRequestException("match_winner is required to finalize a match")

        normalized_event_rows = []
        for event in events:
            recorded_at = event.recorded_at
            try:
                if isinstance(recorded_at, (int, float)):
                    timestamp = float(recorded_at)
                    if abs(timestamp) > 10_000_000_000:
                        timestamp /= 1000
                    recorded_at = datetime.fromtimestamp(
                        timestamp, tz=timezone.utc
                    ).replace(tzinfo=None)
                elif recorded_at is not None and recorded_at.tzinfo is not None:
                    recorded_at = recorded_at.astimezone(timezone.utc).replace(
                        tzinfo=None
                    )
            except (ValueError, OverflowError, OSError) as exc:
                raise BadRequestException(
                    "Invalid event recorded_at timestamp"
                ) from exc
            normalized_event_rows.append(
                {
                    "event_number": event.event_number,
                    "event_type": (
                        event.event_type.value
                        if hasattr(event.event_type, "value")
                        else event.event_type
                    ),
                    "player": event.player,
                    "server": event.server,
                    "elapsed_seconds": event.elapsed_seconds,
                    "recorded_at": recorded_at,
                }
            )

        with transaction(db, "finalize tennis match"):
            match = MatchService.get_match_by_id(db, match_id, for_update=True)
            if match.winner or match.status == "COMPLETED":
                raise ConflictException("Match is already completed")
            if MatchRepository.has_match_events(
                db, match.id
            ) or MatchRepository.get_match_sets(db, match.id):
                raise ConflictException("Match already has persisted sets or events")
            MatchService._validate_final_state(match, data)

            MatchRepository.update_match(
                db,
                match,
                {
                    "player1_points": data.final_state.player1_points,
                    "player2_points": data.final_state.player2_points,
                    "is_tiebreak": data.final_state.is_tiebreak,
                    "tiebreak_player1_points": data.final_state.tiebreak_player1_points,
                    "tiebreak_player2_points": data.final_state.tiebreak_player2_points,
                    "player1_games": data.final_state.player1_games,
                    "player2_games": data.final_state.player2_games,
                    "player1_sets": data.final_state.player1_sets,
                    "player2_sets": data.final_state.player2_sets,
                    "winner": data.final_state.match_winner,
                    "status": "COMPLETED",
                    "serving_state": data.final_state.serving_state,
                },
                commit=False,
            )

            for index, set_data in enumerate(data.final_state.completed_sets, start=1):
                MatchRepository.add_match_set(
                    db,
                    {
                        "match_id": match.id,
                        "set_number": index,
                        "player1_games": set_data.player1_games,
                        "player2_games": set_data.player2_games,
                        "was_tiebreak": set_data.was_tiebreak,
                        "tiebreak_player1_points": set_data.tiebreak_player1_points,
                        "tiebreak_player2_points": set_data.tiebreak_player2_points,
                        "serving_state": set_data.serving_state,
                    },
                    commit=False,
                )

            MatchRepository.create_match_events(db, match.id, normalized_event_rows)

        return MatchService.get_scoreboard(db, match_id)
