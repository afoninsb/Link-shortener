from datetime import datetime, timedelta
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
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


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


async def get_password_hash(password):
    return pwd_context.hash(password)


async def get_user(username: str, db: AsyncSession):
    user = await db.execute(select(User).where(User.username == username))
    return user.scalar_one_or_none()


async def authenticate_user(username: str, password: str, db: AsyncSession):
    user = await get_user(username, db)
    return user if await verify_password(
        password, user.hashed_password) else False


async def create_access_token(
        data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=app_settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode,
        app_settings.secret_key,
        app_settings.algorithm
    )


async def get_current_user(token: str = Depends(oauth2_scheme),
                           db: AsyncSession = Depends(get_session)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            app_settings.secret_key,
            algorithms=[app_settings.algorithm]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = users_schemas.TokenData(username=username)
    except JWTError as e:
        raise credentials_exception from e
    user = await get_user(token_data.username, db)
    if user is None:
        raise credentials_exception
    return jsonable_encoder(user)


async def create_user(
    obj_in: users_schemas.UserAuth, db: AsyncSession
):
    """ Создает нового пользователя в БД """
    obj_in_data = jsonable_encoder(obj_in)
    hashed_password = await get_password_hash(obj_in_data['password'])
    db_obj = User(
        username=obj_in_data['username'],
        hashed_password=hashed_password
    )
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj
