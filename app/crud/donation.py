from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import User
from app.models.donation import Donation
from app.schemas.donation import DonationCreate


class CRUDReservation(CRUDBase[Donation, DonationCreate, None]):
    """
    CRUD для модели Donation
    """

    async def get_by_user(
        self,
        session: AsyncSession,
        user: User,
    ) -> list[Donation]:
        """
        Получение списка пожертвований, сделанных пользователем
        :param user: Модель пользователя для фильтрации
        :param session: Асинхронная сессия
        :return: Список отфильтрованных объектов модели Donation
        """
        donations = await session.execute(
            select(Donation).where(Donation.user_id == user.id)
        )
        return donations.scalars().all()


donation_crud = CRUDReservation(Donation)
