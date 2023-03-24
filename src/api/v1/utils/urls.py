from typing import Any, Union

from fastapi import Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.schemas import urls as urls_schemas
from api.v1.utils.utils import Paginator, to_short_id
from core.config import app_settings
from db.db import get_session
from db.models import Transition, Url


async def create_url(obj_in: urls_schemas.UrlCreate,
                     db: AsyncSession,
                     user: dict[str, Union[str, int]] | None
                     ) -> Url:
    """Сохранение новой ссылки."""
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
                          ) -> None:
    """Сохранение информации о переходе."""
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
                  ) -> Url:
    """Оформляем переход по ссылке."""
    url = await db.execute(select(Url).where(Url.id == url_id))
    url = url.scalar_one_or_none()
    await save_transition(url, db, user)
    return url


async def del_url(url: Url, db: AsyncSession,) -> Url:
    """Отмечаем ссылку удалённой."""
    url.is_deleted = True
    await db.commit()
    return url


async def is_private_url(url: Url,
                         obj_in: urls_schemas.UrlIsPrivate,
                         db: AsyncSession) -> Url:
    """Меняем видимость ссылки."""
    obj_in_data = jsonable_encoder(obj_in)
    url.is_private = obj_in_data['is_private']
    await db.commit()
    return url


async def get_url_info(url_id: int,
                       db: AsyncSession = Depends(get_session),
                       ) -> Any:
    not_found_exception = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
    )
    """Возвращаем информацию о ссылке."""
    url = await db.execute(select(Url).where(Url.id == url_id))
    if url := url.scalar_one_or_none():
        return url
    else:
        raise not_found_exception


async def status_url(url_id: int,
                     params: dict[str, int],
                     db: AsyncSession = Depends(get_session),
                     ):
    """Возвращаем информацию о переходах по ссылке."""
    transitions = (await db.execute(
        select(Transition).where(Transition.url_id == url_id)
    )).scalars().all()
    if not params:
        return {
            'total': len(transitions),
            'pages': 1,
            'size': len(transitions),
            'page': 1,
            'items': transitions
        }
    paginator = Paginator(page=params['page'], size=params['size'])
    # a = (await db.execute(select(Transition).where(Transition.url_id == url_id).join(Transition.user))).scalars().all()
    # for b in a:
    #     print(jsonable_encoder(b))
    return paginator.paginate(transitions)
