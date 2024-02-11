from sqlalchemy import Column, ForeignKey, Integer, Text

from app.models.base import BaseTable


class Donation(BaseTable):
    user_id = Column(
        Integer, ForeignKey("user.id", name="fk_reservation_user_id_user")
    )
    comment = Column(Text)
