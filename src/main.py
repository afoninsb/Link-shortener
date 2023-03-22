from fastapi import FastAPI, Depends
from fastapi.responses import ORJSONResponse

from core.config import app_settings
from api.v1.routers import urls, users
# from api.v1.utils import check_allowed_ip


app = FastAPI(
    title=app_settings.app_title,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
    # dependencies=[Depends(check_allowed_ip)]
)

app.include_router(urls.router, prefix='/api/v1')
app.include_router(users.router, prefix='/api/v1')
