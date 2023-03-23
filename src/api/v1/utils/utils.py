from fastapi import Depends, Header, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from api.v1.schemas import users as users_schemas
from core.config import app_settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class Paginator:
    def __init__(self, offset: int = 0, limit: int = 10):
        self.offset = offset
        self.limit = limit

    def __str__(self):
        return (f'{self.__class__.__name__}: offset: {self.offset}, '
                f'limit: {self.limit}')


async def check_allowed_ip(request: Request):
    def is_ip_banned(headers):
        is_banned = False
        try:
            real_ip = headers["X-REAL-IP"]
            print(real_ip)
            is_banned = real_ip in app_settings.black_list
        except KeyError:
            print("IP header not found")
            is_banned = True
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
