import os
from logging import config as logging_config
from pathlib import Path
from typing import Tuple

from pydantic import BaseSettings, PostgresDsn

from core.logger import LOGGING

logging_config.dictConfig(LOGGING)

BASE_DIR = Path(__file__).resolve().parent.parent


class AppSettings(BaseSettings):
    app_title: str = 'library'
    db: str = 'postgres'
    db_user: str = 'postgres'
    db_password: str = 'postgres'
    db_host: str = 'localhost'
    db_port: int = 5432
    database_dsn: PostgresDsn = (
        f'postgresql+asyncpg://{db_user}:{db_password}'
        f'@{db_host}:{db_port}/{db}'
    )
    short_url: str
    secret_key: str
    algorithm: str = 'HS256'
    access_token_expire_minutes: int = 15
    black_list: Tuple[str, ...] = ('127.0.1.1',)
    testing: bool

    class Config:
        env_file = os.path.join(BASE_DIR, '.env')


app_settings = AppSettings()
