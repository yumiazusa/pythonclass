from pydantic import BaseModel, Field

from app.schemas.user import UserPublic


class LoginRequest(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=6, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserPublic


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=6, max_length=128)
    new_password: str = Field(min_length=6, max_length=128)
    confirm_password: str = Field(min_length=6, max_length=128)


class ChangePasswordResponse(BaseModel):
    message: str
    user: UserPublic


class UpdateProfileRequest(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    full_name: str | None = Field(default=None, max_length=64)


class UpdateProfileResponse(BaseModel):
    message: str
    user: UserPublic
