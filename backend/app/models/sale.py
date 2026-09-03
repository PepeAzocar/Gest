import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.customer import Customer
from app.models.mixins import UUIDPKMixin
from app.models.product import Product
from app.models.warehouse import Warehouse


class SaleStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    PENDING_PAYMENT = "PENDING_PAYMENT"
    PAID = "PAID"
    CANCELLED = "CANCELLED"
    REFUNDED = "REFUNDED"


class PaymentStatus(str, enum.Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    REFUNDED = "REFUNDED"


class SalesChannel(str, enum.Enum):
    STORE = "STORE"
    WEBSITE = "WEBSITE"
    MERCADOLIBRE = "MERCADOLIBRE"
    INSTAGRAM = "INSTAGRAM"
    WHATSAPP = "WHATSAPP"
    FAIR = "FAIR"
    DIRECT = "DIRECT"


class Sale(UUIDPKMixin, Base):
    __tablename__ = "sales"

    sale_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)

    customer_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("customers.id"), nullable=True
    )
    warehouse_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("warehouses.id"), nullable=False
    )

    sale_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False, default=SaleStatus.PAID.value)

    subtotal: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    discount_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    tax_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    total_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)

    payment_status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=PaymentStatus.PENDING.value
    )
    payment_method: Mapped[str | None] = mapped_column(String(50))

    sales_channel: Mapped[str] = mapped_column(String(20), nullable=False)

    notes: Mapped[str | None] = mapped_column(Text)

    created_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    items: Mapped[list["SaleItem"]] = relationship(
        back_populates="sale", cascade="all, delete-orphan", lazy="selectin"
    )
    customer: Mapped["Customer | None"] = relationship(lazy="selectin")
    warehouse: Mapped["Warehouse"] = relationship(lazy="selectin")


class SaleItem(UUIDPKMixin, Base):
    __tablename__ = "sale_items"

    sale_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sales.id", ondelete="CASCADE"), nullable=False
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("products.id"), nullable=False
    )

    quantity: Mapped[float] = mapped_column(Numeric(12, 3), nullable=False)

    unit_price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    discount_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    subtotal: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)

    product_cost: Mapped[float | None] = mapped_column(Numeric(12, 2))
    margin: Mapped[float | None] = mapped_column(Numeric(12, 2))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    sale: Mapped["Sale"] = relationship(back_populates="items")
    product: Mapped["Product"] = relationship(lazy="selectin")
