from datetime import datetime, timedelta
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Header, Request, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select

from api.v1.schemas import users as users_schemas
from core.config import app_settings
from db.models import User
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from db.db import get_session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class Paginator:
    def __init__(self, offset: int = 0, limit: int = 10):
        self.offset = offset
        self.limit = limit

    def __str__(self):
        return (f'{self.__class__.__name__}: offset: {self.offset}, '
                f'limit: {self.limit}')


async def verify_token(authorization: str = Header()):
    def is_valid(token: str) -> bool:
        if "Bearer" not in token:
            return False
        # get token and validate
        return True

    if not is_valid(authorization):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization")


async def check_allowed_ip(request: Request):
    def is_ip_banned(headers):
        is_banned = False
        try:
            real_ip = headers["X-REAL-IP"]
            print(real_ip)
            is_banned = real_ip in app_settings.black_list
        except KeyError:
            print("IP header not found")
            is_banned = True
        return is_banned

    if is_ip_banned(request.headers):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)


ALPHABET = '1234567890qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM'
ALPHABET_LENGTH = len(ALPHABET)


def to_short_id(n: int) -> str:
    if n < ALPHABET_LENGTH:
        return ALPHABET[n]

    return to_short_id(n // ALPHABET_LENGTH) + ALPHABET[n % ALPHABET_LENGTH]


def is_auth(func, token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        headers={"WWW-Authenticate": "Bearer"},
    )

    def wrapper():
        is_auth = False
        print(111111111111111111111111, token)
        if isinstance(token, str):
            try:
                payload = jwt.decode(
                    token,
                    app_settings.secret_key,
                    algorithms=[app_settings.algorithm]
                )
                username: str = payload.get("sub")
                if username is None:
                    raise credentials_exception
                if users_schemas.TokenData(username=username):
                    is_auth = True
            except JWTError as e:
                raise credentials_exception from e
        func(is_auth=is_auth)
    return wrapper
