from pydantic import BaseModel, Field, model_validator
from typing import Optional, List, Literal
from datetime import date, time

PlayerSlot = Literal["PLAYER1", "PLAYER2"]
IndividualPlayerSlot = Literal["PLAYER1", "PLAYER2", "PLAYER3", "PLAYER4"]
MatchFormat = Literal["BEST_OF_3", "BEST_OF_5"]
MatchType = Literal["SINGLES", "DOUBLES"]
PointType = Literal[
    "NORMAL", "ACE", "WINNER", "FORCED_ERROR",
    "UNFORCED_ERROR", "DOUBLE_FAULT", "FAULT"
]


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

            if len(self.service_order) != 4:
                raise ValueError("service_order must contain 4 players")

            if len(set(self.service_order)) != 4:
                raise ValueError("service_order must not contain duplicates")

            if set(self.service_order) != {
                "PLAYER1", "PLAYER2", "PLAYER3", "PLAYER4"
            }:
                raise ValueError(
                    "service_order must contain PLAYER1, PLAYER2, PLAYER3 and PLAYER4"
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

    @model_validator(mode="after")
    def validate_service_order(self):
        # service_order is optional during update.
        # Empty list means "no doubles service-order update".
        if self.service_order:
            if (
                    len(self.service_order) != 4
                    or len(set(self.service_order)) != 4
                    or set(self.service_order) != {
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


class PointCreate(BaseModel):
    winner: PlayerSlot
    point_type: PointType = "NORMAL"
    remarks: Optional[str] = Field(None, max_length=255)


class SetScoreResponse(BaseModel):
    set_number: int
    player1_games: int
    player2_games: int
    was_tiebreak: bool
    tiebreak_player1_points: Optional[int] = None
    tiebreak_player2_points: Optional[int] = None

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