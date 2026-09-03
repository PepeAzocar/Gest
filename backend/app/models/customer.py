from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base
from app.models.mixins import TimestampMixin, UUIDPKMixin


class Customer(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "customers"

    customer_type: Mapped[str] = mapped_column(String(20), nullable=False, default="PERSON")

    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str | None] = mapped_column(String(100))

    rut: Mapped[str | None] = mapped_column(String(20), unique=True)
    email: Mapped[str | None] = mapped_column(String(150))
    phone: Mapped[str | None] = mapped_column(String(30))

    address: Mapped[str | None] = mapped_column(String(255))
    commune: Mapped[str | None] = mapped_column(String(100))
    region: Mapped[str | None] = mapped_column(String(100))

    notes: Mapped[str | None] = mapped_column(Text)

    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
