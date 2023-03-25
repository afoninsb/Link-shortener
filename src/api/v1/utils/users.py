from datetime import datetime, timedelta
from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.schemas import users as users_schemas
from api.v1.utils.utils import Paginator
from core.config import app_settings
from db.db import get_session
from db.models import Url, User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)


async def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяем правильность введённого пароля."""
    return pwd_context.verify(plain_password, hashed_password)


async def get_password_hash(password: str) -> str:
    """Хешируем пароль."""
    return pwd_context.hash(password)


async def get_user(username: str, db: AsyncSession) -> User:
    """Возвращаем информацию о пользователе."""
    user = await db.execute(select(User).where(User.username == username))
    return user.scalar_one_or_none()


async def authenticate_user(username: str,
                            password: str,
                            db: AsyncSession
                            ) -> User | bool:
    """Аутентификация пользователя."""
    user = await get_user(username, db)
    if user and verify_password(password, user.hashed_password):
        return user
    return False


async def create_access_token(data: dict,
                              expires_delta:
                              timedelta | None = None
                              ) -> str:
    """Получение токена авторизации."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=app_settings.access_token_expire_minutes)
    to_encode["exp"] = expire
    return jwt.encode(
        to_encode,
        app_settings.secret_key,
        app_settings.algorithm
    )


async def get_current_user(token: str = Depends(oauth2_scheme),
                           db: AsyncSession = Depends(get_session)
                           ) -> dict[str, str | int] | None:
    """Проверка наличия и правильности токена авториазции."""
    if not token:
        return None
    try:
        payload = jwt.decode(
            token,
            app_settings.secret_key,
            algorithms=[app_settings.algorithm]
        )
        username: str = payload.get("sub")
        if username is None:
            return None
        token_data = users_schemas.TokenData(username=username)
    except JWTError:
        return None
    user = await get_user(token_data.username, db)
    return None if user is None else jsonable_encoder(user)


async def unauthorized(token: str = Depends(oauth2_scheme),
                       db: AsyncSession = Depends(get_session)
                       ) -> Any:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        headers={"WWW-Authenticate": "Bearer"},
    )
    """Если токена нет или не верен, вызываем 401_UNAUTHORIZED."""
    user = await get_current_user(token, db)
    if not user:
        raise credentials_exception
    return user


async def create_user(obj_in: users_schemas.UserAuth,
                      db: AsyncSession
                      ) -> User:
    """Создает нового пользователя в БД."""
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


async def status_user(current_user: dict[str, str | int],
                      params: dict[str, int],
                      db: AsyncSession = Depends(get_session),
                      ):
    """Возвращаем информацию о ссылках пользователя."""
    urls = (await db.execute(
        select(Url).where(Url.user_id == current_user['id'])
    )).scalars().all()
    if not params:
        return {
            'total': len(urls),
            'pages': 1,
            'size': len(urls),
            'page': 1,
            'items': urls
        }
    paginator = Paginator(page=params['page'], size=params['size'])
    return paginator.paginate(urls)
