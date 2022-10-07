from pydantic import BaseModel
from fastapi import Query


class ShowUser(BaseModel):
    fullname: str
    h_index: int
    url: str
    document_count: int | None = None
    citation_count: int | None = None

    class Config():
        orm_mode = True


class ShowSortUser(BaseModel):
    fullname: str
    h_index: int
    url: str

    class Config():
        orm_mode = True


class User(BaseModel):
    guid: str = Query(
        default='00000000-0000-0000-0000-000000000002',
        alias="Уникальный UUID идентификатор научного сотрудника",
        regex='^\d{8}-\d{4}-\d{4}-\d{4}-\d{12}$'
    )
    fullname: str = Query(
        default='Иванов Василий Андреевич',
        alias="ФИО научного сотрудника",
        regex='^[А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]+(?:\s+[А-ЯЁ][а-яё]+)$'

    )
    scientometric_database: str = Query(
        default='scopus',
        alias="Источник данных (Scopus, WOS, RISC)",
        regex='^(?:scopus|wos|risc)$'
    )
    document_count: int = Query(
        default=303,
        alias="Количество публикаций автора, проиндексированных источником",
        ge=0
    )
    citation_count: int = Query(
        default=1140,
        alias="Количество цитирований автора",
        ge=0
    )
    h_index: int = Query(
        default=14,
        alias="Индекс Хирша, рассчитанный НБД",
        ge=0
    )
    url: str = Query(
        default='https://www.scopus.com/authid/detail.uri?authorId=7404809618',
        alias="Ссылка на профиль автора в НБД",
        regex='^https:\\/\\/(elibrary.ru\\/project_author_tools.asp\\?|www.webofscience.com\\/wos\\/woscc\\/basic-search|www.scopus.com\\/authid\\/detail.uri\\?authorId\\=\d+)$'
    )

    class Config():
        orm_mode = True
