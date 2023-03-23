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
    database_dsn: PostgresDsn
    short_url: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    black_list: Tuple[str, ...] = ('123.34.234.23',)

    class Config:
        env_file = os.path.join(BASE_DIR, '.env')


app_settings = AppSettings()
