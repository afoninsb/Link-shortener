import logging
from datetime import timedelta
from logging import config as logging_config
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.schemas import users as users_schemas
from api.v1.utils import users as users_utils
from core.config import app_settings
from core.logger import LOGGING
from db.db import get_session
from db.models import User

logging_config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    '/user/signup',
    response_model=users_schemas.UserOut,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"description": "Username уже существует"},
    }
)
async def create_user(
    data: users_schemas.UserAuth,
    db: AsyncSession = Depends(get_session)
) -> Any:
    """Регистрация пользователя."""
    user = await users_utils.get_user(data.username, db)
    if user is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username уже существует"
        )
    new_user = await users_utils.create_user(data, db)
    logger.info(f'New user registered {new_user.username}')
    return jsonable_encoder(new_user)


@router.post(
    "/user/login",
    response_model=users_schemas.Token,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"description": "Не авторизован"},
    }
)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_session),
) -> Any:
    """Авторизация - получение токена авторизации."""
    user = await users_utils.authenticate_user(
        form_data.username, form_data.password, db)
    if not user:
        logger.info('Wrong authorization')
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(
        minutes=app_settings.access_token_expire_minutes)
    access_token = await users_utils.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    logger.info(f'User logged in {user.username}')
    return {"access_token": access_token, "token_type": "bearer"}


@router.get(
    "/user/me",
    response_model=users_schemas.UserOut,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"description": "Не авторизован"},
    }
)
async def user_me(
    current_user: User = Depends(users_utils.unauthorized),
) -> Any:
    """Информация о текущем пользователе."""
    logger.info(f'User information requested {current_user["username"]}')
    return current_user


@router.get(
    '/user/status',
    response_model=users_schemas.UserStatus,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"description": "Не авторизован"},
    }
)
async def get_user_status(
    page: int | None = 0,
    size: int | None = 10,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(users_utils.unauthorized),
) -> Any:
    """Статус пользователя."""
    params = {'page': page, 'size': size} if page and size else {}
    logger.info(f'User status requested {current_user["username"]}')
    return await users_utils.status_user(
        current_user,
        db=db,
        params=params
    )
