from datetime import datetime

from pydantic import BaseModel, Extra, Field, PositiveInt, validator


class CharityProjectBase(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None
    full_amount: PositiveInt | None

    class Config:
        extra = Extra.forbid

    @validator("description")
    def name_cannot_be_null(cls, value):
        if value == "":
            raise ValueError("Описание проекта не может быть пустым!")
        return value


class CharityProjectCreate(CharityProjectBase):
    name: str = Field(..., min_length=1, max_length=100)
    description: str
    full_amount: PositiveInt

    @validator("full_amount")
    def name_cannot_be_null(cls, value):
        if value < 1:
            raise ValueError("Сумма пожертвования не может быть менее 1!")
        return value


class CharityProjectCheckedCreate(CharityProjectCreate):
    invested_amount: int
    fully_invested: bool | None
    close_date: datetime | None


class CharityProjectDB(CharityProjectCreate):
    id: int
    invested_amount: int
    fully_invested: bool
    create_date: datetime
    close_date: datetime | None

    class Config:
        orm_mode = True


class CharityProjectUpdate(CharityProjectBase):
    @validator("name")
    def name_cannot_be_null(cls, value):
        if value == "":
            raise ValueError("Имя проекта не может быть пустым!")
        return value


class CharityProjectCheckedUpdate(CharityProjectUpdate):
    invested_amount: int | None
    fully_invested: bool | None
    close_date: datetime | None
