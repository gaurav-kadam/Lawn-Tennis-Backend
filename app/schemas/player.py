from pydantic import BaseModel, Field
from typing import Optional


MOBILE_PATTERN = r"^[0-9]{10}$"


class PlayerCreate(BaseModel):
    player_name: str = Field(..., min_length=1, max_length=150)
    age: Optional[int] = Field(default=None, ge=5, le=100)
    gender: str = Field(..., min_length=1, max_length=20)
    weight: Optional[float] = Field(default=None, gt=0)
    category: Optional[str] = Field(default=None, min_length=1, max_length=50)
    state: str = Field(..., min_length=1, max_length=100)
    city: str = Field(..., min_length=1, max_length=100)
    mobile: Optional[str] = Field(default=None, pattern=MOBILE_PATTERN)
    ranking: Optional[int] = Field(default=None, ge=1)

class PlayerUpdate(BaseModel):
    player_name: Optional[str] = Field(default=None, min_length=1, max_length=150)
    age: Optional[int] = Field(default=None, ge=5, le=100)
    gender: Optional[str] = Field(default=None, min_length=1, max_length=20)
    weight: Optional[float] = Field(default=None, gt=0)
    category: Optional[str] = Field(default=None, min_length=1, max_length=50)
    state: Optional[str] = Field(default=None, min_length=1, max_length=100)
    city: Optional[str] = Field(default=None, min_length=1, max_length=100)
    mobile: Optional[str] = Field(default=None, pattern=MOBILE_PATTERN)
    ranking: Optional[int] = Field(default=None, ge=1)
    is_active: Optional[bool] = None

class PlayerResponse(BaseModel):

    id: int
    player_name: str
    player_code: str

    age: Optional[int] = None
    gender: str

    weight: Optional[float] = None
    category: Optional[str] = None

    state: str
    city: str
    mobile: Optional[str] = None
    ranking: Optional[int] = None
    is_active: bool

    class Config:
        from_attributes = True