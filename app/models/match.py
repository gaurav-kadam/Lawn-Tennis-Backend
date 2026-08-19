from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Date,
    Time,
    ForeignKey,
    JSON,
)
from typing import Optional, List, Literal
from datetime import date, time
from sqlalchemy.orm import relationship

from app.db.base import Base


class Match(Base):
    __tablename__ = "matches"

    # ============================================================
    # PRIMARY KEY
    # ============================================================

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    # ============================================================
    # TOURNAMENT
    # ============================================================

    tournament_code = Column(
        String(50),
        ForeignKey("tournament.tournament_code"),
        nullable=True,
    )

    # ============================================================
    # MATCH INFORMATION
    # ============================================================

    match_no = Column(
        String(50),
        nullable=True,
    )

    court_no = Column(
        String(50),
        nullable=True,
    )

    round_name = Column(
        String(100),
        nullable=True,
    )

    gender = Column(
        String(50),
        nullable=True,
    )

    # ============================================================
    # MATCH TYPE
    # ============================================================

    match_type = Column(
        String(10),
        nullable=False,
        default="SINGLES",
        server_default="SINGLES",
    )

    # ============================================================
    # DATE / TIME
    # ============================================================

    match_date = Column(
        Date,
        nullable=True,
    )

    match_time = Column(
        Time,
        nullable=True,
    )

    # ============================================================
    # CATEGORY
    # ============================================================

    match_category = Column(
        String(100),
        nullable=True,
    )

    age_category = Column(
        String(100),
        nullable=True,
    )

    # ============================================================
    # PLAYER 1
    # ============================================================

    player1_id = Column(
        Integer,
        ForeignKey("players.id"),
        nullable=True,
    )

    player1_name = Column(
        String(150),
        nullable=False,
    )

    # ============================================================
    # PLAYER 2
    # ============================================================

    player2_id = Column(
        Integer,
        ForeignKey("players.id"),
        nullable=True,
    )

    player2_name = Column(
        String(150),
        nullable=False,
    )

    # ============================================================
    # DOUBLES PLAYER 3
    # ============================================================

    player3_id = Column(
        Integer,
        ForeignKey("players.id"),
        nullable=True,
    )

    player3_name = Column(
        String(150),
        nullable=True,
    )

    # ============================================================
    # DOUBLES PLAYER 4
    # ============================================================

    player4_id = Column(
        Integer,
        ForeignKey("players.id"),
        nullable=True,
    )

    player4_name = Column(
        String(150),
        nullable=True,
    )

    # ============================================================
    # DOUBLES SERVICE ORDER
    #
    # Example:
    #
    # [
    #     "PLAYER1",
    #     "PLAYER3",
    #     "PLAYER2",
    #     "PLAYER4"
    # ]
    #
    # Singles = []
    # ============================================================

    service_order = Column(
        JSON,
        nullable=False,
        default=list,
        server_default="[]",
    )

    # ============================================================
    # OFFICIALS
    # ============================================================

    digital_scorer_id = Column(
        Integer,
        ForeignKey("officials.id"),
        nullable=True,
    )

    referee_1_id = Column(
        Integer,
        ForeignKey("officials.id"),
        nullable=True,
    )

    referee_2_id = Column(
        Integer,
        ForeignKey("officials.id"),
        nullable=True,
    )

    # Existing compatibility field
    umpire_id = Column(
        Integer,
        ForeignKey("officials.id"),
        nullable=True,
    )

    # ============================================================
    # MATCH FORMAT
    # ============================================================

    match_format = Column(
        String(20),
        nullable=False,
        default="BEST_OF_3",
        server_default="BEST_OF_3",
    )

    # ============================================================
    # MATCH STATUS
    # ============================================================

    status = Column(
        String(20),
        nullable=False,
        default="SCHEDULED",
        server_default="SCHEDULED",
    )

    # ============================================================
    # SERVER
    #
    # The tennis engine works with two scoring sides:
    #
    # PLAYER1
    # PLAYER2
    #
    # For doubles, current_server calculates the individual
    # player from service_order.
    # ============================================================

    first_server = Column(
        String(10),
        nullable=False,
        default="PLAYER1",
        server_default="PLAYER1",
    )

    server = Column(
        String(10),
        nullable=False,
        default="PLAYER1",
        server_default="PLAYER1",
    )

    # ============================================================
    # CURRENT POINTS
    # ============================================================

    player1_points = Column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    player2_points = Column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    # ============================================================
    # TIEBREAK
    # ============================================================

    is_tiebreak = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default="0",
    )

    tiebreak_player1_points = Column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    tiebreak_player2_points = Column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    # ============================================================
    # GAMES
    # ============================================================

    player1_games = Column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    player2_games = Column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    # ============================================================
    # SETS
    # ============================================================

    player1_sets = Column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    player2_sets = Column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    # ============================================================
    # WINNER
    # ============================================================

    winner = Column(
        String(10),
        nullable=True,
    )

    # ============================================================
    # ACTIVE / SOFT DELETE
    # ============================================================

    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        server_default="1",
    )

    is_deleted = Column(
        Boolean,
        default=False,
        nullable=False,
        server_default="0",
    )

    deleted_at = Column(
        DateTime,
        nullable=True,
    )

    deleted_by = Column(
        Integer,
        nullable=True,
    )

    # ============================================================
    # RELATIONSHIPS
    # ============================================================

    sets = relationship(
        "MatchSet",
        back_populates="match",
        order_by="MatchSet.set_number",
    )

    logs = relationship(
        "MatchPointLog",
        back_populates="match",
        order_by="MatchPointLog.point_number",
    )

    # ============================================================
    # CURRENT SERVER
    # ============================================================

    @property
    def current_server(self) -> str:
        if (
                self.match_type != "DOUBLES"
                or not self.service_order
        ):
            return self.server

        # --------------------------------------------------------
        # DOUBLES
        # --------------------------------------------------------

        completed_games = sum(
            (
                    s.player1_games +
                    s.player2_games
            )
            for s in self.sets
        )

        current_set_games = (
                (self.player1_games or 0) +
                (self.player2_games or 0)
        )

        total_games = (
                completed_games +
                current_set_games
        )

        order = self.service_order

        if not order:
            return self.server

        return order[
            total_games % len(order)
            ]


# ================================================================
# MATCH SET
# ================================================================

class MatchSet(Base):
    __tablename__ = "match_sets"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    match_id = Column(
        Integer,
        ForeignKey("matches.id"),
        nullable=False,
    )

    set_number = Column(
        Integer,
        nullable=False,
    )

    player1_games = Column(
        Integer,
        nullable=False,
    )

    player2_games = Column(
        Integer,
        nullable=False,
    )

    was_tiebreak = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default="0",
    )

    tiebreak_player1_points = Column(
        Integer,
        nullable=True,
    )

    tiebreak_player2_points = Column(
        Integer,
        nullable=True,
    )

    match = relationship(
        "Match",
        back_populates="sets",
    )


# ================================================================
# MATCH POINT LOG
# ================================================================

class MatchPointLog(Base):
    __tablename__ = "match_point_logs"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    match_id = Column(
        Integer,
        ForeignKey("matches.id"),
        nullable=False,
    )

    point_number = Column(
        Integer,
        nullable=False,
    )

    set_number = Column(
        Integer,
        nullable=False,
    )

    game_number = Column(
        Integer,
        nullable=False,
    )

    # PLAYER1 / PLAYER2
    winner = Column(
        String(10),
        nullable=False,
    )

    # PLAYER1 / PLAYER2
    server = Column(
        String(10),
        nullable=False,
    )

    point_type = Column(
        String(20),
        nullable=False,
        default="NORMAL",
        server_default="NORMAL",
    )

    player1_score_after = Column(
        String(10),
        nullable=True,
    )

    player2_score_after = Column(
        String(10),
        nullable=True,
    )

    remarks = Column(
        String(255),
        nullable=True,
    )

    created_at = Column(
        DateTime,
        nullable=True,
    )

    match = relationship(
        "Match",
        back_populates="logs",
    )