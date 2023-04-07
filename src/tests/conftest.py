import asyncio
import os
from asyncio import AbstractEventLoop
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from faker import Faker
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

os.environ['TESTING'] = 'True'

import db.models as Models
from core.config import app_settings
from main import app

db_name = "testdb"
database_dsn = (
    f'postgresql://{app_settings.db_user}:'
    f'{app_settings.db_password}@{app_settings.db_host}'
    f':{app_settings.db_port}/{db_name}'
)

fake = Faker()


@pytest.fixture(scope="session")
def engine():
    return create_engine(database_dsn, echo=False)


@pytest.fixture(scope="session")
def tables(engine):
    Models.Base.metadata.create_all(engine)
    yield
    Models.Base.metadata.drop_all(engine)


@pytest.fixture
async def dbsession(engine, tables):
    """Returns an sqlalchemy session,
    and after the test tears down everything properly.
    """
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        app=app,
        follow_redirects=False,
        base_url='http://localhost/api/v1/'
    ) as async_client:
        yield async_client


@pytest.fixture(scope="session")
def event_loop() -> Generator[AbstractEventLoop, None, None]:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


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
        for _ in range(2)
    ]
