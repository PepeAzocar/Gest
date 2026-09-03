import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    Computed,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.mixins import UUIDPKMixin
from app.models.product import Product
from app.models.warehouse import Warehouse


class MovementType(str, enum.Enum):
    INITIAL_STOCK = "INITIAL_STOCK"
    PRODUCTION = "PRODUCTION"
    SALE = "SALE"
    SALE_CANCEL = "SALE_CANCEL"
    RETURN = "RETURN"
    RESERVATION = "RESERVATION"
    RESERVATION_RELEASE = "RESERVATION_RELEASE"
    ADJUSTMENT_IN = "ADJUSTMENT_IN"
    ADJUSTMENT_OUT = "ADJUSTMENT_OUT"
    DAMAGE = "DAMAGE"
    WASTE = "WASTE"
    TRANSFER_IN = "TRANSFER_IN"
    TRANSFER_OUT = "TRANSFER_OUT"


# Movement types that increase / decrease quantity_on_hand directly.
# SALE, RESERVATION and RESERVATION_RELEASE are reserved for the sales module (Phase 3)
# and are intentionally not driven through the generic adjustment endpoint.
INCREASES_ON_HAND = {
    MovementType.INITIAL_STOCK,
    MovementType.PRODUCTION,
    MovementType.RETURN,
    MovementType.ADJUSTMENT_IN,
    MovementType.TRANSFER_IN,
    MovementType.SALE_CANCEL,
}
DECREASES_ON_HAND = {
    MovementType.SALE,
    MovementType.ADJUSTMENT_OUT,
    MovementType.DAMAGE,
    MovementType.WASTE,
    MovementType.TRANSFER_OUT,
}

MANUAL_ADJUSTMENT_TYPES = {
    MovementType.INITIAL_STOCK,
    MovementType.PRODUCTION,
    MovementType.RETURN,
    MovementType.ADJUSTMENT_IN,
    MovementType.ADJUSTMENT_OUT,
    MovementType.DAMAGE,
    MovementType.WASTE,
}


class Inventory(UUIDPKMixin, Base):
    __tablename__ = "inventory"
    __table_args__ = (
        UniqueConstraint("product_id", "warehouse_id", name="uq_inventory_product_warehouse"),
        CheckConstraint("quantity_on_hand >= 0", name="ck_inventory_on_hand_non_negative"),
        CheckConstraint("quantity_reserved >= 0", name="ck_inventory_reserved_non_negative"),
    )

    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )
    warehouse_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("warehouses.id", ondelete="CASCADE"), nullable=False
    )

    quantity_on_hand: Mapped[float] = mapped_column(Numeric(12, 3), default=0, nullable=False)
    quantity_reserved: Mapped[float] = mapped_column(Numeric(12, 3), default=0, nullable=False)
    quantity_available: Mapped[float] = mapped_column(
        Numeric(12, 3),
        Computed("quantity_on_hand - quantity_reserved", persisted=True),
    )

    minimum_stock: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    critical_stock: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    product: Mapped["Product"] = relationship(lazy="selectin")
    warehouse: Mapped["Warehouse"] = relationship(lazy="selectin")


class InventoryMovement(UUIDPKMixin, Base):
    __tablename__ = "inventory_movements"

    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("products.id"), nullable=False, index=True
    )
    warehouse_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("warehouses.id"), nullable=False, index=True
    )

    movement_type: Mapped[str] = mapped_column(String(30), nullable=False)

    quantity: Mapped[float] = mapped_column(Numeric(12, 3), nullable=False)

    stock_before: Mapped[float] = mapped_column(Numeric(12, 3), nullable=False)
    stock_after: Mapped[float] = mapped_column(Numeric(12, 3), nullable=False)

    reference_type: Mapped[str | None] = mapped_column(String(30))
    reference_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))

    reason: Mapped[str | None] = mapped_column(Text)

    movement_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    created_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
