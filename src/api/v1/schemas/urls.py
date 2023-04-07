from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class UrlCreate(BaseModel):
    original: str
    description: str
    is_private: bool


class UrlBase(BaseModel):
    id: UUID
    description: str
    original: str
    short: str
    is_private: bool
    is_deleted: bool

    class Config:
        orm_mode = True


class UrlIsPrivate(BaseModel):
    is_private: bool


class TrinsitUser(BaseModel):
    id: int
    username: str

    class Config:
        orm_mode = True


class Transitions(BaseModel):
    date: datetime
    user: TrinsitUser | None

    class Config:
        orm_mode = True


class TransistionsList(BaseModel):
    total: int
    pages: int
    size: int
    page: int
    items: list[Transitions | None] = None

    class Config:
        orm_mode = True


class UrlStatus(BaseModel):
    id: UUID
    transitions: TransistionsList


class DBStatus(BaseModel):
    status: str
