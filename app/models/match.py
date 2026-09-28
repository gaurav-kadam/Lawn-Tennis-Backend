from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Time, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.base import Base


class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)

    tournament_code = Column(String(50), ForeignKey("tournament.tournament_code"), nullable=True)

    match_no = Column(String(50), nullable=True)
    court_no = Column(String(50), nullable=True)
    round_name = Column(String(100), nullable=True)
    gender = Column(String(50), nullable=True)

    match_type = Column(String(10), nullable=False, default="SINGLES", server_default="SINGLES")

    match_date = Column(Date, nullable=True)
    match_time = Column(Time, nullable=True)

    match_category = Column(String(100), nullable=True)
    age_category = Column(String(100), nullable=True)

    player1_id = Column(Integer, ForeignKey("players.id"), nullable=True)
    player1_name = Column(String(150), nullable=False)

    player2_id = Column(Integer, ForeignKey("players.id"), nullable=True)
    player2_name = Column(String(150), nullable=False)

    player3_id = Column(Integer, ForeignKey("players.id"), nullable=True)
    player3_name = Column(String(150), nullable=True)

    player4_id = Column(Integer, ForeignKey("players.id"), nullable=True)
    player4_name = Column(String(150), nullable=True)

    service_order = Column(JSON, nullable=False, default=list, server_default="[]")
    serving_state = Column(JSON, nullable=True)

    digital_scorer_id = Column(Integer, ForeignKey("officials.id"), nullable=True)
    referee_1_id = Column(Integer, ForeignKey("officials.id"), nullable=True)
    referee_2_id = Column(Integer, ForeignKey("officials.id"), nullable=True)
    umpire_id = Column(Integer, ForeignKey("officials.id"), nullable=True)

    match_format = Column(String(20), nullable=False, default="BEST_OF_3", server_default="BEST_OF_3")

    status = Column(String(20), nullable=False, default="SCHEDULED", server_default="SCHEDULED")

    first_server = Column(String(10), nullable=False, default="PLAYER1", server_default="PLAYER1")
    server = Column(String(10), nullable=False, default="PLAYER1", server_default="PLAYER1")

    player1_points = Column(Integer, nullable=False, default=0, server_default="0")
    player2_points = Column(Integer, nullable=False, default=0, server_default="0")

    is_tiebreak = Column(Boolean, nullable=False, default=False, server_default="0")

    tiebreak_player1_points = Column(Integer, nullable=False, default=0, server_default="0")
    tiebreak_player2_points = Column(Integer, nullable=False, default=0, server_default="0")

    player1_games = Column(Integer, nullable=False, default=0, server_default="0")
    player2_games = Column(Integer, nullable=False, default=0, server_default="0")

    player1_sets = Column(Integer, nullable=False, default=0, server_default="0")
    player2_sets = Column(Integer, nullable=False, default=0, server_default="0")

    winner = Column(String(10), nullable=True)

    is_active = Column(Boolean, default=True, nullable=False, server_default="1")
    is_deleted = Column(Boolean, default=False, nullable=False, server_default="0")

    deleted_at = Column(DateTime, nullable=True)
    deleted_by = Column(Integer, nullable=True)

    sets = relationship("MatchSet", back_populates="match", order_by="MatchSet.set_number")
    events = relationship("MatchEvent", back_populates="match", order_by="MatchEvent.event_number")


class MatchSet(Base):
    __tablename__ = "match_sets"
    __table_args__ = (
        UniqueConstraint(
            "match_id",
            "set_number",
            name="uq_match_sets_match_id_set_number",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False)

    set_number = Column(Integer, nullable=False)
    player1_games = Column(Integer, nullable=False)
    player2_games = Column(Integer, nullable=False)

    was_tiebreak = Column(Boolean, nullable=False, default=False, server_default="0")

    tiebreak_player1_points = Column(Integer, nullable=True)
    tiebreak_player2_points = Column(Integer, nullable=True)

    serving_state = Column(JSON, nullable=True)

    match = relationship("Match", back_populates="sets")


class MatchEvent(Base):
    __tablename__ = "match_events"
    __table_args__ = (
        UniqueConstraint(
            "match_id",
            "event_number",
            name="uq_match_events_match_id_event_number",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False, index=True)

    event_number = Column(Integer, nullable=False)
    event_type = Column(String(30), nullable=False)
    player = Column(String(10), nullable=False)
    server = Column(String(10), nullable=True)

    elapsed_seconds = Column(Integer, nullable=False, default=0, server_default="0")
    recorded_at = Column(DateTime, nullable=True)

    match = relationship("Match", back_populates="events")