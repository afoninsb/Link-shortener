import os

import asyncpg
import pytest
import pytest_asyncio

from src.core.config import app_settings

os.environ['TESTING'] = 'True'

import asyncio
from asyncio import AbstractEventLoop
from typing import AsyncGenerator, Generator

import asyncpg
import pytest
import pytest_asyncio
from faker import Faker
from httpx import AsyncClient

import src.db.db as DB
import src.db.models as Models
from src.main import app

DSN = (
    f'postgresql://{app_settings.db_user}:'
    f'{app_settings.db_password}@{app_settings.db_host}'
    f':{app_settings.db_port}/'
)

fake = Faker()


@pytest_asyncio.fixture(scope='function')
async def client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        app=app,
        follow_redirects=False,
        base_url='http://localhost/api/v1/'
    ) as async_client:
        yield async_client


@pytest.fixture(scope="session")
def event_loop() -> Generator[AbstractEventLoop, None, None]:
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


async def temp_db() -> None:
    dsn_1 = f'{DSN}{app_settings.db}'
    conn = await asyncpg.connect(dsn_1)
    sql_command = (
        f'CREATE DATABASE {DB.db_name} OWNER {app_settings.db_user};'
    )
    await conn.execute(sql_command)
    await conn.close()


@pytest_asyncio.fixture(scope="function")
async def create_db():
    await temp_db()
    async with DB.engine.begin() as conn:
        await conn.run_sync(Models.Base.metadata.drop_all)
        await conn.run_sync(Models.Base.metadata.create_all)
    await DB.engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def dropdb():
    dsn = f'{DSN}{app_settings.db}'
    conn = await asyncpg.connect(dsn)
    sql_command = (
        "UPDATE pg_database SET datallowconn = 'false' "
        f"WHERE datname = '{DB.db_name}';"
    )
    await conn.execute(sql_command)
    sql_command = (
        "SELECT pg_terminate_backend(pg_stat_activity.pid) "
        "FROM pg_stat_activity "
        f"WHERE pg_stat_activity.datname = '{DB.db_name}' "
        "AND pid <> pg_backend_pid();"
    )
    await conn.execute(sql_command)
    sql_command = f'DROP DATABASE {DB.db_name};'
    await conn.execute(sql_command)
    await conn.close()


@pytest_asyncio.fixture(scope='function')
async def user_data():
    return {
        'password': fake.password(length=12),
        'username': fake.simple_profile()['username'],
    }


@pytest_asyncio.fixture(scope='function')
async def urls_data():
    return [
        {
            'original': fake.uri(),
            'description': fake.sentence(nb_words=5),
            'is_private': False
        }
        for _ in range(3)
    ]
