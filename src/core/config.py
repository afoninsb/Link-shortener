import os
from pydantic import BaseSettings, PostgresDsn
from logging import config as logging_config
from pathlib import Path
from typing import Tuple
from core.logger import LOGGING

logging_config.dictConfig(LOGGING)

BASE_DIR = Path(__file__).resolve().parent.parent


class AppSettings(BaseSettings):
    app_title: str = 'library'
    database_dsn: PostgresDsn
    black_list: Tuple[str, ...] = ('123.34.234.23',)

    class Config:
        env_file = os.path.join(BASE_DIR, '.env')


app_settings = AppSettings()
