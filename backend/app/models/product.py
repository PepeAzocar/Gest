from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.mixins import TimestampMixin, UUIDPKMixin


class ProductCategory(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "product_categories"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    products: Mapped[list["Product"]] = relationship(back_populates="category")


class Product(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "products"

    sku: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    category_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("product_categories.id"), nullable=True
    )

    length_cm: Mapped[float | None] = mapped_column(Numeric(8, 2))
    width_cm: Mapped[float | None] = mapped_column(Numeric(8, 2))
    height_cm: Mapped[float | None] = mapped_column(Numeric(8, 2))
    weight_kg: Mapped[float | None] = mapped_column(Numeric(8, 3))

    recommended_age_min: Mapped[int | None] = mapped_column(Integer)
    recommended_age_max: Mapped[int | None] = mapped_column(Integer)

    requires_adult_supervision: Mapped[bool | None] = mapped_column(Boolean)

    main_material: Mapped[str | None] = mapped_column(String(100))
    paint_type: Mapped[str | None] = mapped_column(String(100))
    finish_type: Mapped[str | None] = mapped_column(String(100))

    non_toxic_paint: Mapped[bool | None] = mapped_column(Boolean)
    handmade: Mapped[bool | None] = mapped_column(Boolean)

    production_time_hours: Mapped[float | None] = mapped_column(Numeric(8, 2))

    minimum_stock: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    critical_stock: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    category: Mapped["ProductCategory | None"] = relationship(back_populates="products")
    images: Mapped[list["ProductImage"]] = relationship(
        back_populates="product",
        order_by="ProductImage.position",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class ProductImage(UUIDPKMixin, Base):
    __tablename__ = "product_images"

    product_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True
    )
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    position: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    product: Mapped["Product"] = relationship(back_populates="images")

    @property
    def url(self) -> str:
        return f"/uploads/products/{self.product_id}/{self.filename}"
