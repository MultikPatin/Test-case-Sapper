from datetime import datetime
from typing import TypeVar

from sqlalchemy import false, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import CharityProject, Donation

T = TypeVar("T", CharityProject, Donation)


async def get_not_full_invested_objects(
    session: AsyncSession,
    obj_in: T,
) -> list[T]:
    """
    Возвращает список не инвестированных объектов
    :param session: Асинхронная сессия
    :param obj_in: Модель для определения БД
    :return: Список не инвестированных объектов
    """
    target = CharityProject if isinstance(obj_in, Donation) else Donation
    objects = await session.execute(
        select(target)
        .where(target.fully_invested == false())
        .order_by("create_date")
    )
    return objects.scalars().all()


def close_donation_for_obj(obj_in: T):
    """
    Задание полей закрытия объекта
    :param obj_in: Обновляемый объект
    :return: Объект с откорректированными полями
    """
    obj_in.invested_amount = obj_in.full_amount
    obj_in.fully_invested = True
    obj_in.close_date = datetime.now()
    return obj_in


def invest_money(
    obj_in: T,
    obj_model: T,
) -> tuple[T, T]:
    """
    Инвестирование и определение объектов для закрытия
    :param obj_in: Созданный объект
    :param obj_model: Не инвестированный объект
    :return:
    """
    free_amount_in = obj_in.full_amount - obj_in.invested_amount
    free_amount_in_model = obj_model.full_amount - obj_model.invested_amount

    if free_amount_in > free_amount_in_model:
        obj_in.invested_amount += free_amount_in_model
        close_donation_for_obj(obj_model)
    elif free_amount_in == free_amount_in_model:
        close_donation_for_obj(obj_in)
        close_donation_for_obj(obj_model)
    else:
        obj_model.invested_amount += free_amount_in
        close_donation_for_obj(obj_in)

    return obj_in, obj_model


async def investing_process(
    session: AsyncSession,
    obj_in: T,
) -> T:
    """
    Расчёт инвестирования
    :param session: Асинхронная сессия
    :param obj_in: Созданный объект
    :return: Созданный объект с откорректированными полями
    """
    objects_model = await get_not_full_invested_objects(session, obj_in)

    for model in objects_model:
        obj_in, model = invest_money(obj_in, model)
        session.add(obj_in)
        session.add(model)

    await session.commit()
    await session.refresh(obj_in)
    return obj_in
