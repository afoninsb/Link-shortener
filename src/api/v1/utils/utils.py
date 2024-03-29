import contextlib
from typing import Any

from fastapi import HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer

from core.config import app_settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class Paginator:
    def __init__(self, page: int = 0, size: int = 10):
        self.page = page
        self.size = size

    def __str__(self):
        return (f'{self.__class__.__name__}: offset: {self.offset}, '
                f'limit: {self.limit}')

    def paginate(self, content: list[Any]) -> dict[str, int | list[Any]]:
        length = len(content)
        if length % self.size == 0:
            pages = length // self.size
        else:
            pages = (length // self.size) + 1
        start = (self.page - 1) * self.size
        end = self.page * self.size
        return {
            'total': length,
            'pages': pages,
            'size': self.size,
            'page': self.page,
            'items': content[start: end]
        }


async def check_allowed_ip(request: Request):
    def is_ip_banned(headers):
        is_banned = False
        with contextlib.suppress(KeyError):
            real_ip = headers["X-REAL-IP"]
            print(real_ip)
            is_banned = real_ip in app_settings.black_list
        return is_banned

    if is_ip_banned(request.headers):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)


ALPHABET = '1234567890qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM'
ALPHABET_LENGTH = len(ALPHABET)


def to_short_id(n: int) -> str:
    """Сокращатель url."""
    if n < ALPHABET_LENGTH:
        return ALPHABET[n]

    return to_short_id(n // ALPHABET_LENGTH) + ALPHABET[n % ALPHABET_LENGTH]
