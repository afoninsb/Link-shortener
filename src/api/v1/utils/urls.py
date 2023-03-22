from sqlalchemy import select
from api.v1.schemas import urls as urls_schemas
from db.models import Url
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.encoders import jsonable_encoder

from api.v1.utils.utils import to_short_id
from core.config import app_settings


async def create_url(
    obj_in: urls_schemas.UrlCreate,
    db: AsyncSession,
):
    """ Создает нового пользователя в БД """
    max_id_obj = await db.execute(select(Url).order_by(-Url.id))
    if max_id_obj := max_id_obj.scalar_one_or_none():
        max_id = max_id_obj.Url.id + 1
    else:
        max_id = 1
    obj_in_data = jsonable_encoder(obj_in)
    db_obj = Url(**obj_in_data)
    db_obj.short = f'{app_settings.short_url}{to_short_id(max_id)}'
    db_obj.id = max_id
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def get_url(url_id: int, db: AsyncSession,):
    """ Возвращает информацию о пользователе """
    results = await db.execute(select(Url).where(Url.id == url_id))
    return results.scalar_one_or_none()
