from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import charity_project
from app.core.db import get_async_session
from app.core.user import current_superuser
from app.crud.charity_project import charity_project_crud
from app.schemas.charity_project import (
    CharityProjectCreate,
    CharityProjectDB,
    CharityProjectUpdate,
)
from app.services.investment_fund import investing_process

router = APIRouter()


@router.get(
    "/",
    response_model=list[CharityProjectDB],
    response_model_exclude_none=True,
)
async def get_all_charity_projects(
    session: AsyncSession = Depends(get_async_session),
):
    """
    Получает список всех проектов.
    """
    return await charity_project_crud.get_multi(session)


@router.post(
    "/",
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
)
async def create_new_meeting_room(
    obj_in: CharityProjectCreate,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Создает благотворительный проект.
    Только для супер юзеров.
    """
    await charity_project.is_duplicate(session, obj_in.name)

    new_project = await charity_project_crud.create(session, obj_in)
    return await investing_process(session, new_project)


@router.patch(
    "/{project_id}",
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)],
)
async def partially_update_charity_project(
    project_id: int,
    obj_in: CharityProjectUpdate,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Изменить параметры проекта.
    Закрытый проект нельзя редактировать, также нельзя установить требуемую сумму меньше уже вложенной.
    Только для супер юзеров.
    """
    project = await charity_project.is_exists(session, project_id)

    await charity_project.is_duplicate(session, obj_in.name)
    await charity_project.is_closed(session, project_id)
    await charity_project.is_full_amount_update_correct(
        session, project_id, obj_in.full_amount
    )
    return await charity_project_crud.update(session, project, obj_in)


@router.delete(
    "/{project_id}",
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)],
)
async def remove_charity_project(
    project_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Удаляет проект.
    Нельзя удалить проект, в который уже были инвестированы средства, его можно только закрыть.
    Только для супер юзеров.
    """
    project = await charity_project.is_exists(session, project_id)
    await charity_project.has_donations(session, project_id)
    return await charity_project_crud.remove(session, project)
