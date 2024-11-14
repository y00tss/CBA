from pydantic import BaseModel


class ArticleCreateRequest(BaseModel):
    title: str
    magazine_id: int

    class Config:
        orm_mode = True


class ArticleUpdateRequest(BaseModel):
    title: str
    magazine_id: int

    class Config:
        orm_mode = True
