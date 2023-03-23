from datetime import datetime
from typing import List, Union

from pydantic import BaseModel

from api.v1.schemas import users as users_schemas


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


class UrlIsPrivate(BaseModel):
    is_private: bool


class Transitions(BaseModel):
    date: datetime
    user_id: int | None


class TransistionsList(BaseModel):
    total: int
    pages: int
    page: int
    size: int
    items: List[Union[Transitions, None]] = None


class UrlStatus(BaseModel):
    id: int
    transitions: TransistionsList
