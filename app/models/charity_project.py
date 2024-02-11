from sqlalchemy import Column, String, Text

from app.models.base import BaseTable


class CharityProject(BaseTable):
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
