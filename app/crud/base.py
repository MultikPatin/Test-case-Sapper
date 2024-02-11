from typing import Generic, TypeVar

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import Base
from app.models import User

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Базовый класс CRUD операций
    """

    def __init__(self, model: type[ModelType]):
        self.model = model

    async def get(
        self,
        session: AsyncSession,
        obj_id: int,
    ) -> ModelType | None:
        """
        Получение одного объекта по id
        :param obj_id: Первичный ключ
        :param session: Асинхронная сессия
        :return: Найденный объект
        """
        db_obj = await session.execute(
            select(self.model).where(self.model.id == obj_id)
        )
        return db_obj.scalars().first()

    async def get_multi(
        self,
        session: AsyncSession,
    ) -> list[ModelType]:
        """
        Получение списка всех объектов
        :param session: Асинхронная сессия
        :return: Список найденных объектов
        """
        db_objs = await session.execute(select(self.model))
        return db_objs.scalars().all()

    async def create(self, session: AsyncSession, obj_in, user: User | None):
        """
        Создание объекта
        :param obj_in: Данные для создания
        :param session: Асинхронная сессия
        :param user: Объект пользователя (опциональный)
        :return: Созданный объект
        """
        obj_in_data = obj_in.dict()
        if user is not None:
            obj_in_data["user_id"] = user.id
        db_obj = self.model(**obj_in_data)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def update(
        self,
        session: AsyncSession,
        db_obj: ModelType,
        obj_in: UpdateSchemaType,
    ) -> ModelType:
        """
        Обновление объекта
        :param db_obj: Объект модели для обновления
        :param obj_in: Данные для обновления
        :param session: Асинхронная сессия
        :return: Обновлённый объект
        """
        obj_data = jsonable_encoder(db_obj)
        update_data = obj_in.dict(exclude_unset=True)

        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def remove(
        self,
        session: AsyncSession,
        db_obj: ModelType,
    ) -> ModelType:
        """
        Удаление объекта
        :param db_obj: Объект модели для удаления
        :param session:  Асинхронная сессия
        :return: Удалённый объект
        """
        await session.delete(db_obj)
        await session.commit()
        return db_obj
