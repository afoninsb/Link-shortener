from fastapi import Request, Header, HTTPException, status

from core.config import app_settings


class Paginator:
    def __init__(self, offset: int = 0, limit: int = 10):
        self.offset = offset
        self.limit = limit

    def __str__(self):
        return (f'{self.__class__.__name__}: offset: {self.offset}, '
                f'limit: {self.limit}')


async def verify_token(authorization: str = Header()):
    def is_valid(token: str) -> bool:
        if "Bearer" not in token:
            return False
        # get token and validate
        return True

    if not is_valid(authorization):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization")


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
