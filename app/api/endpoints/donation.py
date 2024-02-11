from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_superuser, current_user
from app.crud.donation import donation_crud
from app.models import User
from app.schemas.donation import DonationAdminDB, DonationCreate, DonationDB
from app.services.investment_fund import investing_process

router = APIRouter()


@router.get(
    "/",
    response_model=list[DonationAdminDB],
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
)
async def get_all_donations(
    session: AsyncSession = Depends(get_async_session),
):
    """
    Получает список всех пожертвований.
    Только для супер юзеров.
    """
    return await donation_crud.get_multi(session)


@router.post(
    "/",
    response_model=DonationDB,
    response_model_exclude_none=True,
)
async def create_donation(
    obj_in: DonationCreate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
):
    new_donation = await donation_crud.create(session, obj_in, user)
    return await investing_process(session, new_donation)


@router.get(
    "/my",
    response_model=list[DonationDB],
    response_model_exclude={"user_id"},
)
async def get_my_donations(
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
):
    """
    Получить список всех пожертвований пользователя.
    Только для авторизованного пользователя.
    """
    return await donation_crud.get_by_user(
        session=session,
        user=user,
    )
