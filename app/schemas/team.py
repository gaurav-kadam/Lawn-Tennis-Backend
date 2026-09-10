from pydantic import BaseModel, Field
from typing import Optional


class TeamCreate(BaseModel):
    team_name: str = Field(..., min_length=1, max_length=150)
    short_name: str = Field(..., min_length=1, max_length=50)

    gender: str = Field(..., min_length=1, max_length=20)

    state: str = Field(..., min_length=1, max_length=100)
    city: str = Field(..., min_length=1, max_length=100)

    section: str = Field(..., min_length=1, max_length=100)

    head_coach: str = Field(..., min_length=1, max_length=150)
    coach: str = Field(..., min_length=1, max_length=150)
    manager: str = Field(..., min_length=1, max_length=150)

    player_file: Optional[str] = None


class TeamUpdate(BaseModel):
    team_name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=150,
    )

    short_name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=50,
    )

    gender: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=20,
    )

    state: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    city: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    section: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    head_coach: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=150,
    )

    coach: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=150,
    )

    manager: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=150,
    )
    player_file: Optional[str] = None
    is_active: Optional[bool] = None

class TeamResponse(BaseModel):
    id: int
    team_code: str
    team_name: str
    short_name: str
    gender: str
    state: str
    city: str
    section: str
    head_coach: str
    coach: str
    manager: str
    player_file: Optional[str] = None
    is_active: bool
    class Config:
        from_attributes = True