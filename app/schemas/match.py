from pydantic import BaseModel, Field, model_validator
from typing import Optional, List, Literal
from datetime import date, time, datetime
from enum import Enum

PlayerSlot = Literal["PLAYER1", "PLAYER2"]
IndividualPlayerSlot = Literal["PLAYER1", "PLAYER2", "PLAYER3", "PLAYER4"]
MatchFormat = Literal["BEST_OF_3", "BEST_OF_5"]
MatchType = Literal["SINGLES", "DOUBLES"]


class MatchCreate(BaseModel):
    match_type: MatchType = "SINGLES"

    tournament_code: Optional[str] = None
    match_date: Optional[str] = None
    match_time: Optional[str] = None
    court_no: Optional[str] = None
    match_no: Optional[str] = None
    match_category: Optional[str] = None
    age_category: Optional[str] = None
    gender: Optional[str] = None
    round: Optional[str] = None

    player1_name: str = Field(..., min_length=1, max_length=150)
    player2_name: str = Field(..., min_length=1, max_length=150)
    player1_id: Optional[int] = None
    player2_id: Optional[int] = None

    player3_name: Optional[str] = Field(None, max_length=150)
    player4_name: Optional[str] = Field(None, max_length=150)
    player3_id: Optional[int] = None
    player4_id: Optional[int] = None
    service_order: List[IndividualPlayerSlot] = Field(default_factory=list)
    serving_state: Optional[dict] = None

    match_format: MatchFormat = "BEST_OF_3"

    digital_scorer_id: Optional[int] = None
    referee_1_id: Optional[int] = None
    referee_2_id: Optional[int] = None

    umpire_id: Optional[int] = None
    first_server: PlayerSlot = "PLAYER1"

    @model_validator(mode="after")
    def validate_match(self):
        if self.match_type == "DOUBLES":
            if not self.player3_name or not self.player3_name.strip():
                raise ValueError("player3_name is required for DOUBLES")

            if not self.player4_name or not self.player4_name.strip():
                raise ValueError("player4_name is required for DOUBLES")

            if self.service_order:
                if len(self.service_order) != 4:
                    raise ValueError("service_order must contain 4 players")

                if len(set(self.service_order)) != 4:
                    raise ValueError("service_order must not contain duplicates")

                if set(self.service_order) != {
                    "PLAYER1",
                    "PLAYER2",
                    "PLAYER3",
                    "PLAYER4",
                }:
                    raise ValueError(
                        "service_order must contain PLAYER1, PLAYER2, PLAYER3 and PLAYER4"
                    )
            elif not isinstance(self.serving_state, dict):
                raise ValueError(
                    "DOUBLES requires service_order or serving_state configuration"
                )

        else:
            self.player3_name = None
            self.player4_name = None
            self.player3_id = None
            self.player4_id = None
            self.service_order = []

        return self


class MatchUpdate(BaseModel):
    match_no: Optional[str] = None
    court_no: Optional[str] = None
    round_name: Optional[str] = None
    umpire_id: Optional[int] = None

    match_date: Optional[str] = None
    match_time: Optional[str] = None
    match_category: Optional[str] = None
    age_category: Optional[str] = None
    gender: Optional[str] = None

    digital_scorer_id: Optional[int] = None
    referee_1_id: Optional[int] = None
    referee_2_id: Optional[int] = None

    is_active: Optional[bool] = None

    player3_name: Optional[str] = Field(None, max_length=150)
    player4_name: Optional[str] = Field(None, max_length=150)
    service_order: Optional[List[IndividualPlayerSlot]] = None
    serving_state: Optional[dict] = None

    @model_validator(mode="after")
    def validate_service_order(self):
        if self.service_order:
            if (
                len(self.service_order) != 4
                or len(set(self.service_order)) != 4
                or set(self.service_order)
                != {
                    "PLAYER1",
                    "PLAYER2",
                    "PLAYER3",
                    "PLAYER4",
                }
            ):
                raise ValueError(
                    "service_order must contain PLAYER1, PLAYER2, PLAYER3 and PLAYER4"
                )
        return self


class SetScoreResponse(BaseModel):
    set_number: int
    player1_games: int
    player2_games: int
    was_tiebreak: bool
    tiebreak_player1_points: Optional[int] = None
    tiebreak_player2_points: Optional[int] = None
    serving_state: Optional[dict] = None

    class Config:
        from_attributes = True


class MatchResponse(BaseModel):
    id: int

    tournament_code: Optional[str] = None
    match_date: Optional[date] = None
    match_time: Optional[time] = None
    match_category: Optional[str] = None
    age_category: Optional[str] = None
    gender: Optional[str] = None
    round_name: Optional[str] = None

    match_no: Optional[str] = None
    court_no: Optional[str] = None

    match_type: MatchType = "SINGLES"
    player1_name: str
    player2_name: str
    player3_name: Optional[str] = None
    player4_name: Optional[str] = None

    service_order: List[str] = Field(default_factory=list)
    serving_state: Optional[dict] = None

    match_format: str
    status: str

    digital_scorer_id: Optional[int] = None
    referee_1_id: Optional[int] = None
    referee_2_id: Optional[int] = None
    umpire_id: Optional[int] = None

    server: str
    current_server: str

    player1_points: int
    player2_points: int

    is_tiebreak: bool
    tiebreak_player1_points: int
    tiebreak_player2_points: int

    player1_games: int
    player2_games: int

    player1_sets: int
    player2_sets: int

    winner: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True


class MatchScoreboardResponse(BaseModel):
    match: MatchResponse
    completed_sets: List[SetScoreResponse]
    player1_display_point: str
    player2_display_point: str


class MatchEventType(str, Enum):
    POINT = "POINT"
    ACE = "ACE"
    FAULT = "FAULT"
    DOUBLE_FAULT = "DOUBLE_FAULT"
    SERVE = "SERVE"
    WINNER = "WINNER"
    UNFORCED_ERROR = "UNFORCED_ERROR"
    FORCED_ERROR = "FORCED_ERROR"
    VOLLEY = "VOLLEY"
    NORMAL = "NORMAL"


class FinalMatchEvent(BaseModel):
    event_number: int = Field(..., ge=1)

    event_type: MatchEventType

    player: IndividualPlayerSlot

    server: Optional[IndividualPlayerSlot] = None

    elapsed_seconds: int = Field(
        default=0,
        ge=0,
    )
    recorded_at: Optional[datetime | int | float] = None


class FinalSetState(BaseModel):
    player1_games: int = Field(..., ge=0)
    player2_games: int = Field(..., ge=0)

    was_tiebreak: bool = False

    tiebreak_player1_points: Optional[int] = Field(default=None, ge=0)
    tiebreak_player2_points: Optional[int] = Field(default=None, ge=0)
    serving_state: Optional[dict] = None


class FinalMatchState(BaseModel):
    player1_points: int = Field(..., ge=0)
    player2_points: int = Field(..., ge=0)

    player1_games: int = Field(..., ge=0)
    player2_games: int = Field(..., ge=0)

    player1_sets: int = Field(..., ge=0)
    player2_sets: int = Field(..., ge=0)

    is_tiebreak: bool = False

    tiebreak_player1_points: int = Field(
        default=0,
        ge=0,
    )

    tiebreak_player2_points: int = Field(
        default=0,
        ge=0,
    )

    match_winner: Optional[PlayerSlot] = None

    completed_sets: list[FinalSetState] = Field(default_factory=list)

    serving_state: Optional[dict] = None


class FinalizeMatchRequest(BaseModel):
    final_state: FinalMatchState

    events: List[FinalMatchEvent] = Field(
        ...,
        min_length=1,
    )


class MatchEventResponse(BaseModel):
    id: int
    event_number: int
    event_type: MatchEventType
    player: IndividualPlayerSlot
    server: Optional[IndividualPlayerSlot] = None
    elapsed_seconds: int
    recorded_at: Optional[datetime] = None

    class Config:
        from_attributes = True
