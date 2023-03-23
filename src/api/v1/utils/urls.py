from typing import Union
from fastapi import Depends, HTTPException, status
from sqlalchemy import select, update
from api.v1.schemas import urls as urls_schemas
from api.v1.schemas import transitions as transitions_schemas
from db.models import Transition, Url, User
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.encoders import jsonable_encoder

from api.v1.utils.utils import to_short_id, is_auth
from core.config import app_settings
from api.v1.utils import users as users_utils
from db.db import get_session


async def create_url(
    obj_in: urls_schemas.UrlCreate,
    db: AsyncSession,
    user: dict[str, Union[str, int]] | None
):
    """ Создает нового пользователя в БД """
    max_id_obj = await db.execute(select(Url).order_by(-Url.id))
    if max_id_obj := max_id_obj.first():
        max_id = max_id_obj.Url.id + 1
    else:
        max_id = 1
    obj_in_data = jsonable_encoder(obj_in)
    db_obj = Url(**obj_in_data)
    db_obj.short = f'{app_settings.short_url}{to_short_id(max_id)}'
    db_obj.id = max_id
    if user:
        db_obj.user_id = user['id']
    else:
        db_obj.is_private = False
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def save_transition(url: Url,
                          db: AsyncSession,
                          user: dict[str, Union[str, int]] | None
                          ):
    user_id = user['id'] if user else None
    db_obj = Transition(
        url_id=url.id,
        user_id=user_id
    )
    db.add(db_obj)
    await db.commit()


async def get_url(url_id: int,
                  db: AsyncSession,
                  user: dict[str, Union[str, int]] | None
                  ):
    """ Возвращает информацию о пользователе """
    url = await db.execute(select(Url).where(Url.id == url_id))
    url = url.scalar_one_or_none()
    await save_transition(url, db, user)
    return url


async def del_url(url: Url, db: AsyncSession,):
    """ Возвращает информацию о пользователе """
    url.is_deleted = True
    await db.commit()
    return url


async def is_private_url(url: Url,
                         obj_in: urls_schemas.UrlIsPrivate,
                         db: AsyncSession):
    """ Возвращает информацию о пользователе """
    obj_in_data = jsonable_encoder(obj_in)
    url.is_private = obj_in_data['is_private']
    await db.commit()
    return url


async def get_url_info(url_id: int,
                       db: AsyncSession = Depends(get_session),
                       ):
    not_found_exception = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
    )
    """ Возвращает информацию о пользователе """
    url = (await db.execute(select(Url).where(Url.id == url_id)))
    if url := url.scalar_one_or_none():
        return url
    else:
        raise not_found_exception
