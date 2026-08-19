from pydantic import BaseModel
from typing import Optional
from datetime import date


class TournamentCreate(BaseModel):
    tournament_name: str
    start_date: date
    end_date: date
    state: str
    city: str
    venue: str
    section: str
    gender: str


class TournamentUpdate(BaseModel):
    tournament_name: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    state: Optional[str] = None
    city: Optional[str] = None
    venue: Optional[str] = None
    section: Optional[str] = None
    gender: Optional[str] = None
    is_active: Optional[bool] = None


class TournamentResponse(BaseModel):
    id: int
    tournament_name: str
    start_date: date
    end_date: date
    state: str
    city: str
    venue: str
    section: str
    gender: str
    tournament_code: str
    is_active: bool

    class Config:
        from_attributes = True
