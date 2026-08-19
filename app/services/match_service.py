from sqlalchemy.orm import Session
from app.exceptions import NotFoundException, ConflictException, BadRequestException, transaction
from app.repositories.match_repo import MatchRepository
from app.schemas.match import MatchCreate, MatchUpdate, PointCreate
from app.services import tennis_engine as engine
from app.utils.logger import logger

VALID_POINT_TYPES = {
    "NORMAL", "ACE", "WINNER", "FORCED_ERROR",
    "UNFORCED_ERROR", "DOUBLE_FAULT", "FAULT"
}
VALID_FORMATS = {"BEST_OF_3", "BEST_OF_5"}
VALID_PLAYERS = {"PLAYER1", "PLAYER2"}


class MatchService:

    @staticmethod
    def create_match(db: Session, data: MatchCreate):
        if data.match_format not in VALID_FORMATS:
            raise BadRequestException("match_format must be BEST_OF_3 or BEST_OF_5")

        payload = data.model_dump()

        if "round" in payload:
            payload["round_name"] = payload.pop("round")

        if data.match_type == "DOUBLES":
            first_server = data.service_order[0]
            side = "PLAYER1" if first_server in ("PLAYER1", "PLAYER2") else "PLAYER2"
            payload["first_server"] = side
            payload["server"] = side
        else:
            if data.first_server not in VALID_PLAYERS:
                raise BadRequestException("first_server must be PLAYER1 or PLAYER2")
            payload["server"] = data.first_server

        payload["status"] = "LIVE"

        logger.info(
            f"Creating {data.match_type} match: "
            f"{data.player1_name} vs {data.player2_name}"
        )

        return MatchRepository.create_match(db, payload)

    @staticmethod
    def get_match_by_id(db: Session, match_id: int):
        match = MatchRepository.get_match_by_id(db, match_id)
        if not match:
            raise NotFoundException("Match not found")
        return match

    @staticmethod
    def get_all_matches(db: Session, page: int, page_size: int, status_filter: str | None):
        return MatchRepository.get_all_matches(db, page, page_size, status_filter)

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
    def _recompute_and_sync(db: Session, match, logs):
        winners = [log.winner for log in logs]
        state = engine.compute_match_state(
            match.match_format,
            match.first_server,
            winners,
        )

        MatchRepository.update_match(
            db,
            match,
            {
                "server": state["server"],
                "player1_points": state["player1_points"],
                "player2_points": state["player2_points"],
                "is_tiebreak": state["is_tiebreak"],
                "tiebreak_player1_points": state["tiebreak_player1_points"],
                "tiebreak_player2_points": state["tiebreak_player2_points"],
                "player1_games": state["player1_games"],
                "player2_games": state["player2_games"],
                "player1_sets": state["player1_sets"],
                "player2_sets": state["player2_sets"],
                "winner": state["winner"],
                "status": "COMPLETED" if state["winner"] else "LIVE",
            },
            commit=False,
        )

        existing_sets = MatchRepository.get_match_sets(
            db,
            match.id,
        )

        MatchRepository.delete_match_sets_after(
            db,
            match.id,
            keep_count=len(state["completed_sets"]),
            commit=False,
        )

        for index, set_data in enumerate(
                state["completed_sets"],
                start=1,
        ):
            if index > len(existing_sets):
                MatchRepository.add_match_set(
                    db,
                    {
                        "match_id": match.id,
                        "set_number": index,
                        "player1_games": set_data["player1_games"],
                        "player2_games": set_data["player2_games"],
                        "was_tiebreak": set_data["was_tiebreak"],
                        "tiebreak_player1_points": set_data[
                            "tiebreak_player1_points"
                        ],
                        "tiebreak_player2_points": set_data[
                            "tiebreak_player2_points"
                        ],
                    },
                    commit=False,
                )

        return state

    @staticmethod
    def add_point(db: Session, match_id: int, data: PointCreate):
        match = MatchService.get_match_by_id(db, match_id)

        if match.winner:
            raise ConflictException("Match is already completed")

        if data.winner not in VALID_PLAYERS:
            raise BadRequestException("Invalid winner")

        if data.point_type not in VALID_POINT_TYPES:
            raise BadRequestException("Invalid point type")

        logs = MatchRepository.get_point_logs(
            db,
            match_id,
        )

        winners = [log.winner for log in logs]

        state_before = engine.compute_match_state(
            match.match_format,
            match.first_server,
            winners,
        )

        set_number = len(
            state_before["completed_sets"]
        ) + 1

        game_number = (
                state_before["player1_games"] +
                state_before["player2_games"] +
                1
        )

        server = state_before["server"]

        state_after = engine.apply_point(
            dict(state_before),
            data.winner,
        )

        if state_after["is_tiebreak"]:
            p1_after = str(
                state_after["tiebreak_player1_points"]
            )
            p2_after = str(
                state_after["tiebreak_player2_points"]
            )
        else:
            p1_after, p2_after = engine.display_points(
                state_after["player1_points"],
                state_after["player2_points"],
            )

        with transaction(db, "record tennis point"):
            MatchRepository.add_point_log(
                db,
                {
                    "match_id": match_id,
                    "point_number": len(logs) + 1,
                    "set_number": set_number,
                    "game_number": game_number,
                    "winner": data.winner,
                    "server": server,
                    "point_type": data.point_type,
                    "player1_score_after": p1_after,
                    "player2_score_after": p2_after,
                    "remarks": data.remarks,
                },
                commit=False,
            )

            all_logs = MatchRepository.get_point_logs(
                db,
                match_id,
            )

            state = MatchService._recompute_and_sync(
                db,
                match,
                all_logs,
            )

        return MatchService.get_scoreboard(
            db,
            match_id,
            state,
        )

    @staticmethod
    def undo_last_point(db: Session, match_id: int):
        match = MatchService.get_match_by_id(
            db,
            match_id,
        )

        logs = MatchRepository.get_point_logs(
            db,
            match_id,
        )

        if not logs:
            raise BadRequestException("No points to undo")

        with transaction(db, "undo tennis point"):
            MatchRepository.delete_last_point_log(
                db,
                match_id,
                commit=False,
            )

            remaining = MatchRepository.get_point_logs(
                db,
                match_id,
            )

            state = MatchService._recompute_and_sync(
                db,
                match,
                remaining,
            )

        return MatchService.get_scoreboard(
            db,
            match_id,
            state,
        )

    @staticmethod
    def get_scoreboard(
            db: Session,
            match_id: int,
            state=None,
    ):
        match = MatchService.get_match_by_id(
            db,
            match_id,
        )

        completed_sets = MatchRepository.get_match_sets(
            db,
            match_id,
        )

        if state is None:
            logs = MatchRepository.get_point_logs(
                db,
                match_id,
            )

            winners = [log.winner for log in logs]

            state = engine.compute_match_state(
                match.match_format,
                match.first_server,
                winners,
            )

        if state["is_tiebreak"]:
            p1_display = str(
                state["tiebreak_player1_points"]
            )
            p2_display = str(
                state["tiebreak_player2_points"]
            )
        else:
            p1_display, p2_display = engine.display_points(
                state["player1_points"],
                state["player2_points"],
            )

        return {
            "match": match,
            "completed_sets": completed_sets,
            "player1_display_point": p1_display,
            "player2_display_point": p2_display,
        }

    @staticmethod
    def get_point_logs(db: Session, match_id: int):
        MatchService.get_match_by_id(
            db,
            match_id,
        )
        return MatchRepository.get_point_logs(
            db,
            match_id,
        )