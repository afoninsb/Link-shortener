from typing import List, Union

from pydantic import BaseModel

from api.v1.schemas import urls as urls_schemas


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class User(BaseModel):
    username: str


class UserAuth(User):
    password: str


class UserOut(User):
    id: int


class UserStatus(BaseModel):
    total: int
    pages: int
    size: int
    page: int
    items: List[Union[urls_schemas.UrlBase, None]] = None
