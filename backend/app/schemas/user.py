import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class RoleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    code: str
    name: str
    description: str | None = None


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    first_name: str | None = None
    last_name: str | None = None
    role_codes: list[str] = []


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    username: str
    email: EmailStr
    first_name: str | None = None
    last_name: str | None = None
    active: bool
    last_login: datetime | None = None
    created_at: datetime
    roles: list[RoleRead] = []


class LoginRequest(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
