from typing import Any, List
from hashids import Hashids
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from db.services.url import url_crud
from db.db import get_session
from api.schemas import urls as url_schema

router = APIRouter()


@router.post('/',
             response_model=url_schema.Url,
             status_code=status.HTTP_201_CREATED
             )
async def create_url(
    *,
    db: AsyncSession = Depends(get_session),
    url_in: url_schema.UrlCreate,
) -> Any:
    """
    Create new url.
    """
    hashids = Hashids(
        min_length=5,
        alphabet='abcdefghijklmnopqrstuvwxyz0123456789'
    )
    short = hashids.encode(url_in.original)
    url_in.short = short
    return await url_crud.create(db=db, obj_in=url_in)
