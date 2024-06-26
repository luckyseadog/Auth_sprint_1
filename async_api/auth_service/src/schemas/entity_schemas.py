from enum import Enum
from uuid import UUID

from pydantic import BaseModel

from core.config import settings


class RolePatch(BaseModel):
    title: str | None = None
    description: str | None = None


class UserPatch(BaseModel):
    login: str | None = None
    password: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None


class UserCreate(BaseModel):
    login: str
    email: str
    first_name: str
    last_name: str
    password: str


class UserCredentials(BaseModel):
    login: str
    password: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str


class TokenPairExpired(TokenPair):
    access_exp: int
    refresh_exp: int


class AccessTokenData(BaseModel):
    iss: str
    sub: str
    iat: int
    exp: int
    roles: list[str]


class RefreshTokenData(BaseModel):
    iss: str
    sub: str
    iat: int
    exp: int


class UpdateUserRole(BaseModel):
    role_id: UUID
    user_id: UUID


class RoleEnum(str, Enum):
    role_super_admin = settings.role_super_admin
    role_admin = settings.role_admin
    role_user = settings.role_user
    role_subscriber = settings.role_subscriber
    role_guest = settings.role_guest
