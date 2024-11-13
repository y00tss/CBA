from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ArticleCreateRequest(BaseModel):
    title: str
    magazine_id: int

    class Config:
        orm_mode = True


class ArticleUpdateRequest(BaseModel):
    id: int
    title: str
    magazine_id: int

    class Config:
        orm_mode = True
