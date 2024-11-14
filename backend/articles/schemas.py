from pydantic import BaseModel
from enum import Enum


class RefactorType(str, Enum):
    APA = 'APA'
    Custom = 'Custom'


class ArticleCreateRequest(BaseModel):
    title: str
    magazine_id: int
    refactor_type: RefactorType

    class Config:
        orm_mode = True


class ArticleUpdateRequest(BaseModel):
    title: str
    magazine_id: int
    refactor_type: RefactorType

    class Config:
        orm_mode = True
