from pydantic import BaseModel, ValidationError, validator


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


# class UrlInDBBase(BaseModel):
#     id: int
#     description: str
#     original: str
#     is_private: bool
#     is_deleted: bool
#     created_at: datetime

#     class Config:
#         orm_mode = True


# class Url(UrlInDBBase):
#     short: str
