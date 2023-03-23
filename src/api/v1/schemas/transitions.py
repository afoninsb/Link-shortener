from pydantic import BaseModel, ValidationError, validator


class TransitionCreate(BaseModel):
    url_id: int
    user_id: int
