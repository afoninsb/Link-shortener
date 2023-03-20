from typing import Optional
from datetime import datetime

from pydantic import BaseModel


class UrlBase(BaseModel):
    original: str
    description: str
    is_private: bool


class UrlCreate(UrlBase):
    pass


class UrlInDBBase(BaseModel):
    id: int
    description: str
    original: str
    short: str
    is_private: bool
    created_at: datetime

    class Config:
        orm_mode = True


class Url(UrlInDBBase):
    pass
