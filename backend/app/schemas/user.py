from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

RoleType = Literal["student", "teacher", "admin"]


class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    role: RoleType


class UserCreate(UserBase):
    password: str = Field(min_length=6, max_length=128)


class UserPublic(UserBase):
    id: int
    is_enabled: bool
    must_change_password: bool
    student_no: str | None = None
    class_name: str | None = None
    full_name: str | None = None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
