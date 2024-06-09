from uuid import UUID

from pydantic import BaseModel
from datetime import datetime


class RoleInDB(BaseModel):
    id: UUID
    title: str
    description: str | None = None


class UserCreate(BaseModel):
    login: str
    password: str
    first_name: str
    last_name: str


class UserInDB(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    roles: list[RoleInDB]

    class Config:
        orm_mode = True



class RoleCreate(BaseModel):
    title: str
    description: str | None = None

    class Config:
        orm_mode = True




