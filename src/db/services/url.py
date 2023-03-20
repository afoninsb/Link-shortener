from db.models import Url as UrlModel
from api.schemas.urls import UrlCreate
from .base import RepositoryDB


class RepositoryUrl(RepositoryDB[UrlModel, UrlCreate]):
    pass


url_crud = RepositoryUrl(UrlModel)
