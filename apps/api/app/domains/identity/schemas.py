from typing import Annotated

from pydantic import BaseModel, EmailStr, Field, StringConstraints

Password = Annotated[str, StringConstraints(min_length=12, max_length=128)]


class RegisterRequest(BaseModel):
    email: EmailStr
    password: Password
    display_name: str = Field(min_length=1, max_length=100)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class TokenRequest(BaseModel):
    token: str = Field(min_length=32, max_length=256)


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str = Field(min_length=32, max_length=256)
    new_password: Password


class ProfilePatch(BaseModel):
    display_name: str | None = Field(default=None, min_length=1, max_length=100)
    locale: str | None = Field(default=None, min_length=2, max_length=16)


class UserRead(BaseModel):
    id: str
    email: EmailStr
    email_verified: bool
    display_name: str
    locale: str
