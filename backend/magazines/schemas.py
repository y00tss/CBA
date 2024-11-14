from pydantic import BaseModel


class MagazineCreateRequest(BaseModel):
    title: str
    maximum_articles: int


class MagazineUpdateRequest(BaseModel):
    title: str
    maximum_articles: int
