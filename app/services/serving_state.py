"""Serving-state serialization and compatibility helpers.

The frontend owns live scoring and serving. This module validates and
normalizes serving metadata that is persisted with matches and sets.
"""

from dataclasses import dataclass
from typing import Iterable, Mapping, Optional, Tuple


PLAYER1 = "PLAYER1"
PLAYER2 = "PLAYER2"
PLAYER3 = "PLAYER3"
PLAYER4 = "PLAYER4"

DOUBLES_PLAYERS = frozenset((PLAYER1, PLAYER2, PLAYER3, PLAYER4))
TEAM_A = frozenset((PLAYER1, PLAYER2))
TEAM_B = frozenset((PLAYER3, PLAYER4))


def _validate_player(player: str) -> str:
    if player not in DOUBLES_PLAYERS:
        raise ValueError(f"Unknown player slot: {player}")
    return player


def team_for_player(player: str) -> str:
    _validate_player(player)
    return "TEAM1" if player in TEAM_A else "TEAM2"


def teammate(player: str) -> str:
    _validate_player(player)
    pairs = {
        PLAYER1: PLAYER2,
        PLAYER2: PLAYER1,
        PLAYER3: PLAYER4,
        PLAYER4: PLAYER3,
    }
    return pairs[player]


def _other_singles_player(player: str) -> str:
    if player == PLAYER1:
        return PLAYER2
    if player == PLAYER2:
        return PLAYER1
    raise ValueError(f"Singles server must be PLAYER1 or PLAYER2: {player}")


def _validate_doubles_order(order: Iterable[str]) -> Tuple[str, ...]:
    normalized = tuple(order)
    if len(normalized) != 4 or frozenset(normalized) != DOUBLES_PLAYERS:
        raise ValueError(
            "Doubles service order must contain PLAYER1, PLAYER2, PLAYER3 and PLAYER4"
        )
    return normalized


def _interleaved_doubles_order(first_server: str, opposing_first_server: str) -> Tuple[str, ...]:
    _validate_player(first_server)
    _validate_player(opposing_first_server)
    if team_for_player(first_server) == team_for_player(opposing_first_server):
        raise ValueError("Doubles first servers must belong to opposing teams")
    return (
        first_server,
        opposing_first_server,
        teammate(first_server),
        teammate(opposing_first_server),
    )


@dataclass(frozen=True)
class ServingState:
    """Serving state independent of point-scoring state."""

    match_type: str
    first_server: str
    current_server: str
    current_set_first_server: str
    current_set_service_order: Tuple[str, ...] = ()
    doubles_serve_index: int = 0
    tiebreak_first_server: Optional[str] = None
    is_tiebreak: bool = False

    @property
    def current_serving_team(self) -> str:
        return team_for_player(self.current_server)


def initialize_singles(first_server: str = PLAYER1) -> ServingState:
    _other_singles_player(first_server)
    return ServingState(
        match_type="SINGLES",
        first_server=first_server,
        current_server=first_server,
        current_set_first_server=first_server,
        current_set_service_order=(first_server, _other_singles_player(first_server)),
    )


def initialize_doubles(
    first_server: str,
    opposing_first_server: str,
) -> ServingState:
    order = _interleaved_doubles_order(first_server, opposing_first_server)
    return ServingState(
        match_type="DOUBLES",
        first_server=first_server,
        current_server=first_server,
        current_set_first_server=first_server,
        current_set_service_order=order,
        doubles_serve_index=0,
    )


def initialize_from_config(
    match_type: str,
    first_server: str,
    opposing_first_server: Optional[str] = None,
    service_order: Optional[Iterable[str]] = None,
) -> ServingState:
    """Initialize new-match state from creation configuration."""
    if match_type == "SINGLES":
        return initialize_singles(first_server)
    if match_type != "DOUBLES":
        raise ValueError(f"Unknown match type: {match_type}")
    if opposing_first_server:
        return initialize_doubles(first_server, opposing_first_server)
    if service_order:
        return from_legacy(match_type, first_server, service_order)
    raise ValueError("Doubles creation requires both team first servers")


def from_legacy(
    match_type: str,
    first_server: str,
    service_order: Optional[Iterable[str]] = None,
) -> ServingState:
    """Build state for records created before serving_state was persisted."""
    if match_type == "SINGLES":
        return initialize_singles(first_server)

    if match_type != "DOUBLES":
        raise ValueError(f"Unknown match type: {match_type}")

    if service_order:
        order = _validate_doubles_order(service_order)
        current = order[0]
        return ServingState(
            match_type="DOUBLES",
            first_server=current,
            current_server=current,
            current_set_first_server=current,
            current_set_service_order=order,
            doubles_serve_index=0,
        )

    # Legacy doubles rows without an order only know the scoring side. Keep
    # that side-level value instead of inventing an individual player.
    if first_server not in (PLAYER1, PLAYER2):
        raise ValueError("Legacy doubles first_server must be PLAYER1 or PLAYER2")
    return ServingState(
        match_type="DOUBLES",
        first_server=first_server,
        current_server=first_server,
        current_set_first_server=first_server,
    )


def serving_state_to_dict(state: ServingState) -> Mapping[str, object]:
    return {
        "version": 1,
        "match_type": state.match_type,
        "first_server": state.first_server,
        "current_server": state.current_server,
        "current_set_first_server": state.current_set_first_server,
        "current_set_service_order": list(state.current_set_service_order),
        "doubles_serve_index": state.doubles_serve_index,
        "tiebreak_first_server": state.tiebreak_first_server,
        "is_tiebreak": state.is_tiebreak,
    }


def serving_state_from_dict(data: Mapping[str, object]) -> ServingState:
    order = tuple(data.get("current_set_service_order") or ())
    match_type = str(data.get("match_type") or "SINGLES")
    first_server = str(data.get("first_server"))
    current_server = str(data.get("current_server"))
    current_set_first_server = str(data.get("current_set_first_server") or first_server)
    if match_type == "DOUBLES" and order:
        _validate_doubles_order(order)
    elif match_type == "SINGLES":
        _other_singles_player(first_server)
    return ServingState(
        match_type=match_type,
        first_server=first_server,
        current_server=current_server,
        current_set_first_server=current_set_first_server,
        current_set_service_order=order,
        doubles_serve_index=int(data.get("doubles_serve_index") or 0),
        tiebreak_first_server=data.get("tiebreak_first_server") or None,
        is_tiebreak=bool(data.get("is_tiebreak", False)),
    )
