from typing import Optional
from datetime import date

from pydantic import BaseModel, Field, AliasChoices, EmailStr


MOBILE_PATTERN = r"^[0-9]{10}$"


class OfficialCreate(BaseModel):

    official_name: str = Field(
        ...,
        min_length=1,
        max_length=150,
        validation_alias=AliasChoices(
            "official_name",
            "name",
        ),
    )

    role_title: str = Field(
        default="Official",
        min_length=1,
        max_length=100,
        validation_alias=AliasChoices(
            "role_title",
            "role",
            "designation",
        ),
    )

    mobile: Optional[str] = Field(
        default=None,
        pattern=MOBILE_PATTERN,
        validation_alias=AliasChoices(
            "mobile",
            "phone",
            "phone_no",
        ),
    )

    email: Optional[EmailStr] = None

    state: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )

    city: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )

    date_of_birth: Optional[date] = Field(
        default=None,
        validation_alias=AliasChoices(
            "date_of_birth",
            "dob",
        ),
    )

    gender: Optional[str] = Field(
        default=None,
        max_length=20,
    )


class OfficialUpdate(BaseModel):

    official_name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=150,
        validation_alias=AliasChoices(
            "official_name",
            "name",
        ),
    )

    role_title: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=100,
        validation_alias=AliasChoices(
            "role_title",
            "role",
            "designation",
        ),
    )

    mobile: Optional[str] = Field(
        default=None,
        pattern=MOBILE_PATTERN,
        validation_alias=AliasChoices(
            "mobile",
            "phone",
            "phone_no",
        ),
    )

    email: Optional[EmailStr] = None

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

    date_of_birth: Optional[date] = Field(
        default=None,
        validation_alias=AliasChoices(
            "date_of_birth",
            "dob",
        ),
    )

    gender: Optional[str] = Field(
        default=None,
        max_length=20,
    )

    is_active: Optional[bool] = None


class OfficialResponse(BaseModel):

    id: int

    official_name: str
    official_code: str
    role_title: Optional[str] = "Official"

    mobile: Optional[str] = None
    email: Optional[EmailStr] = None

    state: Optional[str] = None
    city: Optional[str] = None

    date_of_birth: Optional[date] = None
    gender: Optional[str] = None

    is_active: bool

    class Config:
        from_attributes = True