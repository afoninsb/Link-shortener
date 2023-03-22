from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime, timedelta
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from db.db import get_session
from fastapi.encoders import jsonable_encoder

from api.v1.schemas import users as users_schemas
from api.v1.utils import users as users_utils
from core.config import app_settings
from db.models import User

router = APIRouter()


@router.post("/login",
             summary="Create access token for user",
             response_model=users_schemas.Token
             )
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_session),
):
    user = await users_utils.authenticate_user(
        form_data.username, form_data.password, db)
    if not user:
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
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/users/me/", response_model=users_schemas.UserOut)
async def read_users_me(
    current_user: User = Depends(users_utils.get_current_user),
):
    return current_user


@router.post('/signup',
             summary="Create new user",
             response_model=users_schemas.UserOut,
             status_code=status.HTTP_201_CREATED
             )
async def create_user(
    data: users_schemas.UserAuth,
    db: AsyncSession = Depends(get_session)
):
    user = await users_utils.get_user(data.username, db)
    if user is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username уже существует"
        )
    new_user = await users_utils.create_user(data, db)
    return jsonable_encoder(new_user)
