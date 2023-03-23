from typing import List, Union
from pydantic import BaseModel, ValidationError, validator
from datetime import datetime


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


class UrlStatus(BaseModel):
    id: int
    count: int
    transitions: Union[List[Transitions], None] = None
