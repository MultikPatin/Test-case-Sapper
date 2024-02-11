from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.charity_project import charity_project_crud
from app.models import CharityProject


async def is_exists(
    session: AsyncSession,
    project_id: int,
) -> CharityProject:
    """
    Проверяет, существует ли проект с заданным полем id
    :param session: Асинхронная сессия
    :param project_id: Идентификатор проекта
    :return: Найденный объект или None
    """
    charity_project = await charity_project_crud.get(session, project_id)
    if charity_project is None:
        raise HTTPException(status_code=404, detail="Проект не найден!")
    return charity_project


async def is_duplicate(
    session: AsyncSession,
    name: str,
) -> None:
    """
    Проверяет, существует ли проект с заданным полем name
    :param session: Асинхронная сессия
    :param name: Имя проекта
    """
    charity_project_id = await charity_project_crud.get_id_by_name(
        session, name
    )
    if charity_project_id is not None:
        raise HTTPException(
            status_code=400,
            detail="Проект с таким именем уже существует!",
        )


async def is_closed(
    session: AsyncSession,
    project_id: int,
) -> None:
    """
    Генерирует исключение если проект закрыт
    :param session: Асинхронная сессия
    :param project_id: id проекта
    """
    charity_project = await charity_project_crud.get(session, project_id)
    if charity_project.fully_invested:
        raise HTTPException(
            status_code=400,
            detail="Закрытый проект нельзя редактировать!",
        )


async def is_full_amount_update_correct(
    session: AsyncSession,
    project_id: int,
    update_full_amount: int,
) -> None:
    """
    Генерирует исключение если сбора для обновления меньше уже инвестированной
    :param session: Асинхронная сессия
    :param project_id: id проекта
    :param update_full_amount: сумма сбора для обновления
    """
    charity_project = await charity_project_crud.get(session, project_id)

    if (
        update_full_amount is not None
        and update_full_amount < charity_project.invested_amount
    ):
        raise HTTPException(
            status_code=400,
            detail="Нельзя установить сумму меньше уже инвестированной!",
        )


async def has_donations(
    session: AsyncSession,
    project_id: int,
) -> None:
    """
    Генерирует исключение если в проект были инвестированы средства
    :param session: Асинхронная сессия
    :param project_id: id проекта
    """
    charity_project = await charity_project_crud.get(session, project_id)
    if charity_project.invested_amount > 0:
        raise HTTPException(
            status_code=400,
            detail="В проект были внесены средства, не подлежит удалению!",
        )
