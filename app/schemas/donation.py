from datetime import datetime

from pydantic import BaseModel, Extra, PositiveInt, validator


class DonationBase(BaseModel):
    comment: str
    full_amount: PositiveInt

    class Config:
        extra = Extra.forbid


class DonationDB(DonationBase):
    id: int
    create_date: datetime

    class Config:
        orm_mode = True


class DonationAdminDB(DonationDB):
    user_id: int
    invested_amount: int
    fully_invested: bool
    close_date: datetime


class DonationCreate(DonationBase):
    @validator("full_amount")
    def full_amount_must_be_more_than_1(cls, value):
        if value < 1:
            raise ValueError("Сумма пожертвования не может быть менее 1!")
        return value


class DonationCheckedCreate(DonationCreate):
    invested_amount: int
    fully_invested: bool | None
    close_date: datetime | None


class DonationCheckedUpdate(DonationBase):
    user_id: str | None
    invested_amount: int | None
    fully_invested: bool | None
    close_date: datetime | None
