from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from db.db import get_session
from api.v1.schemas import urls as urls_schema
from api.v1.utils import urls as urls_utils
from fastapi.encoders import jsonable_encoder
from sqlalchemy.exc import IntegrityError
from fastapi.responses import JSONResponse
from api.v1.utils import users as users_utils

from db.models import User, Url


router = APIRouter()


@router.post('/',
             response_model=urls_schema.UrlBase,
             status_code=status.HTTP_201_CREATED
             )
async def create_url(
    url_in: urls_schema.UrlCreate,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(users_utils.get_current_user)
) -> Any:
    """
    Create new url.
    """
    try:
        new_url = await urls_utils.create_url(url_in, db, current_user)
    except IntegrityError as e:
        raise HTTPException(
            status_code=400, detail="Такой url уже есть") from e
    return jsonable_encoder(new_url)


@router.get('/{url_id}/')
async def get_url(
    url_id: int,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(users_utils.get_current_user),
    current_url: Url = Depends(urls_utils.get_url_info)
) -> Any:
    """
    Create new url.
    """
    if current_url.is_deleted:
        raise HTTPException(status_code=410, detail="Этот url удалён")
    headers = {'Location': current_url.original}
    return JSONResponse(content='', headers=headers, status_code=307)


@router.get('/{url_id}/status',
            response_model=urls_schema.UrlStatus,
            status_code=status.HTTP_200_OK
            )
async def get_url_status(
    url_id: int,
    full_info: bool | None = None,
    offset: int | None = 0,
    limit: int | None = 10,
    db: AsyncSession = Depends(get_session),
    current_url: Url = Depends(urls_utils.get_url_info)
) -> Any:
    """
    Create new url.
    """
    params = {'offset': offset, 'limit': limit} if full_info else {}
    url_info = await urls_utils.status_url(url_id, db=db, params=params)
    result = {
        'id': url_id,
        'count': url_info['count'],
    }
    if full_info:
        result['transitions'] = url_info['transitions']
    return result


@router.post('/{url_id}/delete/',
             response_model=urls_schema.UrlBase,
             status_code=status.HTTP_200_OK
             )
async def del_url(
    url_id: int,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(users_utils.unauthorized),
    current_url: Url = Depends(urls_utils.get_url_info)
) -> Any:
    """
    Create new url.
    """
    url = await urls_utils.del_url(current_url, db)
    return jsonable_encoder(url)


@router.post('/{url_id}/is_private/',
             response_model=urls_schema.UrlBase,
             status_code=status.HTTP_201_CREATED
             )
async def is_private_url(
    url_id: int,
    url_in: urls_schema.UrlIsPrivate,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(users_utils.unauthorized),
    current_url: Url = Depends(urls_utils.get_url_info)
) -> Any:
    """
    Create new url.
    """
    url = await urls_utils.is_private_url(current_url, url_in, db)
    return jsonable_encoder(url)
