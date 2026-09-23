from datetime import date
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1, max_length=100)


class ProfileUpdate(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=120)
    email: str = Field(..., min_length=5, max_length=120)
    password: Optional[str] = Field(None, min_length=6, max_length=100)

    @field_validator("email")
    @classmethod
    def email_ok(cls, v: str) -> str:
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("Enter a valid email address.")
        return v.strip()


class ClubIn(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    description: str = Field("", max_length=2000)


class MemberIn(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    email: str = Field(..., min_length=5, max_length=120)
    role: str = Field("Member", min_length=2, max_length=60)
    club_id: Optional[int] = None

    @field_validator("email")
    @classmethod
    def email_ok(cls, v: str) -> str:
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("Enter a valid email address.")
        return v.strip().lower()


class EventIn(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    event_date: date
    description: str = Field("", max_length=2000)
    club_id: Optional[int] = None


class RegistrationIn(BaseModel):
    event_id: int
    member_id: int


class AttendanceIn(BaseModel):
    event_id: int
    member_id: int
    status: str = Field("present", pattern="^(present|absent)$")


class AnnouncementIn(BaseModel):
    title: str = Field(..., min_length=2, max_length=160)
    content: str = Field(..., min_length=2, max_length=4000)
    club_id: Optional[int] = None
