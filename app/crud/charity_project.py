from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.charity_project import CharityProject
from app.schemas.charity_project import (
    CharityProjectCreate,
    CharityProjectUpdate,
)


class CRUDCharityProject(
    CRUDBase[CharityProject, CharityProjectCreate, CharityProjectUpdate]
):
    """
    CRUD для модели CharityProject
    """

    async def get_id_by_name(
        self,
        session: AsyncSession,
        name: str,
    ) -> int | None:
        """
        Возвращает идентификатор проекта по имени проекта
        :param session: Асинхронная сессия
        :param name: Имя проекта
        :return: Идентификатор проекта
        """
        project_id = await session.execute(
            select(CharityProject.id).where(CharityProject.name == name)
        )
        project_id = project_id.scalars().first()
        return project_id

    async def get_projects_by_completion_rate(
        self,
        session: AsyncSession,
    ) -> list[dict[str, int]]:
        """
        Возвращает лист со словарями данных закрытых проектов,
        отсортированные по скорости сбора средств:
        от тех, что закрылись быстрее всего, до тех, что долго собирали нужную сумму.
        :param session: Асинхронная сессия
        :return: Лист со словарями данных закрытых проектов
        """
        projects = await session.execute(
            select(CharityProject)
            .where(CharityProject.fully_invested)
            .order_by(
                func.julianday(CharityProject.close_date)  # noqa
                - func.julianday(CharityProject.create_date)  # noqa
            )
        )
        projects = projects.scalars().all()
        return projects


charity_project_crud = CRUDCharityProject(CharityProject)
