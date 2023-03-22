from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from db.db import get_session
from api.v1.schemas import urls as urls_schema
from api.v1.utils import urls as urls_utils
from fastapi.encoders import jsonable_encoder
from sqlalchemy.exc import IntegrityError
from fastapi.responses import JSONResponse


router = APIRouter()


@router.post('/',
             response_model=urls_schema.UrlBase,
             status_code=status.HTTP_201_CREATED
             )
async def create_url(
    url_in: urls_schema.UrlCreate,
    db: AsyncSession = Depends(get_session),
) -> Any:
    """
    Create new url.
    """
    try:
        new_url = await urls_utils.create_url(url_in, db)
    except IntegrityError as e:
        raise HTTPException(
            status_code=400, detail="Такой url уже есть") from e
    return jsonable_encoder(new_url)


@router.get('/{url_id}/')
async def get_url(
    url_id: int,
    db: AsyncSession = Depends(get_session),
) -> Any:
    """
    Create new url.
    """
    url = await urls_utils.get_url(url_id, db)
    if not url:
        raise HTTPException(status_code=404, detail="Нет такого url")
    if url.is_deleted:
        raise HTTPException(status_code=410, detail="Этот url удалён")
    headers = {'Location': url.original}
    return JSONResponse(content='', headers=headers, status_code=307)
    # return jsonable_encoder(url)


@router.post('/{url_id}/delete/',
             response_model=urls_schema.UrlBase,
             status_code=status.HTTP_201_CREATED
             )
async def del_url(
    url_id: int,
    db: AsyncSession = Depends(get_session),
) -> Any:
    """
    Create new url.
    """
    url = await urls_utils.del_url(url_id, db)
    if not url:
        raise HTTPException(status_code=404, detail="Нет такого url")
    return jsonable_encoder(url)


@router.post('/{url_id}/is_private/',
             response_model=urls_schema.UrlBase,
             status_code=status.HTTP_201_CREATED
             )
async def is_private_url(
    url_id: int,
    url_in: urls_schema.UrlIsPrivate,
    db: AsyncSession = Depends(get_session),
) -> Any:
    """
    Create new url.
    """
    url = await urls_utils.is_private_url(url_id, url_in, db)
    if not url:
        raise HTTPException(status_code=404, detail="Нет такого url")
    return jsonable_encoder(url)
