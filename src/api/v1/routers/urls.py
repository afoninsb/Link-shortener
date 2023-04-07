import logging
from logging import config as logging_config
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.schemas import urls as urls_schema
from api.v1.utils import urls as urls_utils
from api.v1.utils import users as users_utils
from core.logger import LOGGING
from db.db import get_session
from db.models import Url, User

logging_config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    '/',
    response_model=urls_schema.UrlBase,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"description": "Такой url уже есть"},
    }
)
async def create_url(
    url_in: urls_schema.UrlCreate,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(users_utils.get_current_user)
) -> Any:
    """Создание новой ссылки."""
    try:
        new_url = await urls_utils.create_url(url_in, db, current_user)
    except IntegrityError as e:
        logger.info(f'Recreating a link {url_in.original}')
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Такой url уже есть") from e
    logger.info(f'Link created {new_url.original} -> {new_url.short}')
    return jsonable_encoder(new_url)


@router.get(
    '/{url_id}',
    status_code=status.HTTP_307_TEMPORARY_REDIRECT,
    responses={
        410: {"description": "Этот url удалён"},
        404: {"description": "Такой url не существует"},
    }
)
async def get_url(
    url_id: UUID,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(users_utils.get_current_user),
    current_url: Url = Depends(urls_utils.get_url_info)
) -> Any:
    """Получение короткой ссылки - переход."""
    if current_url.is_deleted:
        logger.info(f'Removed link requested {current_url.original}')
        raise HTTPException(status_code=status.HTTP_410_GONE,
                            detail="Этот url удалён")
    await urls_utils.get_url(current_url, db, current_user)
    headers = {'Location': current_url.original}
    logger.info(
        f'Following a link {current_url.short} -> {current_url.original}'
    )
    return JSONResponse(content='', headers=headers, status_code=307)


@router.get(
    '/{url_id}/status',
    response_model=urls_schema.UrlStatus,
    status_code=status.HTTP_200_OK,
    responses={
        404: {"description": "Такой url не существует"},
    }
)
async def get_url_status(
    url_id: UUID,
    full_info: bool | None = None,
    page: int | None = 1,
    size: int | None = 10,
    db: AsyncSession = Depends(get_session),
    current_url: Url = Depends(urls_utils.get_url_info)
) -> Any:
    """Статус ссылки."""
    params = {'page': page, 'size': size} if full_info else {}
    url_info = await urls_utils.status_url(url_id, db=db, params=params)
    logger.info(f'Link status requested {current_url.original}')
    return {'id': url_id, 'transitions': url_info}


@router.post(
    '/{url_id}/delete',
    response_model=urls_schema.UrlBase,
    status_code=status.HTTP_201_CREATED,
    responses={
        404: {"description": "Такой url не существует"},
    }
)
async def del_url(
    url_id: UUID,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(users_utils.unauthorized),
    current_url: Url = Depends(urls_utils.get_url_info)
) -> Any:
    """Удаление ссылки."""
    url = await urls_utils.del_url(current_url, db, current_user)
    logger.info(f'Link removed {current_url.original}')
    return jsonable_encoder(url)


@router.post(
    '/{url_id}/is_private',
    response_model=urls_schema.UrlBase,
    status_code=status.HTTP_201_CREATED,
    responses={
        403: {"description": "Вы не можете редактировать этот url"},
        404: {"description": "Такой url не существует"},
    }
)
async def change_link_visibility(
    url_id: UUID,
    url_in: urls_schema.UrlIsPrivate,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(users_utils.unauthorized),
    current_url: Url = Depends(urls_utils.get_url_info)
) -> Any:
    """Изменение видимости ссылки."""
    url = await urls_utils.change_link_visibility(
        current_url,
        url_in,
        db,
        current_user
    )
    logger.info(f'Link visibility changed {current_url.original}')
    return jsonable_encoder(url)


@router.get(
    '/db/ping',
    response_model=urls_schema.DBStatus,
    status_code=status.HTTP_200_OK,
)
async def ping_db(
    db: AsyncSession = Depends(get_session)
) -> dict[str, str]:
    """Статус базы данных."""
    sql = text("SELECT 1;")
    try:
        await db.execute(sql)
    except Exception:
        return {'status': 'База данных не доступна!!!'}
    else:
        return {'status': 'OK'}
