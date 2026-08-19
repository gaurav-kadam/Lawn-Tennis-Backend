from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PointLogResponse(BaseModel):
    id: int
    point_number: int
    set_number: int
    game_number: int
    winner: str
    server: str
    point_type: str
    player1_score_after: Optional[str] = None
    player2_score_after: Optional[str] = None
    remarks: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
