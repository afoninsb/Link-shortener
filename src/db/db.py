from pydantic import PostgresDsn
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from core.config import app_settings

database_dsn: PostgresDsn = (
    f'postgresql+asyncpg://{app_settings.db_user}:'
    f'{app_settings.db_password}@{app_settings.db_host}'
    f':{app_settings.db_port}/{app_settings.db}'
)
engine = create_async_engine(database_dsn, echo=True, future=True)
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
