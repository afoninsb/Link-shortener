from datetime import datetime
from typing import List, Union

from pydantic import BaseModel


class UrlCreate(BaseModel):
    original: str
    description: str
    is_private: bool


class UrlBase(BaseModel):
    id: int
    description: str
    original: str
    short: str
    is_private: bool
    is_deleted: bool

    class Config:
        orm_mode = True


class UrlIsPrivate(BaseModel):
    is_private: bool


class Transitions(BaseModel):
    date: datetime
    user_id: int | None

    class Config:
        orm_mode = True


class TransistionsList(BaseModel):
    total: int
    pages: int
    size: int
    page: int
    items: List[Union[Transitions, None]] = None

    class Config:
        orm_mode = True


class UrlStatus(BaseModel):
    id: int
    transitions: TransistionsList


class DBStatus(BaseModel):
    status: str
    code: int
