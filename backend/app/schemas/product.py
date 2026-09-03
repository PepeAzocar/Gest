import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class ProductCategoryCreate(BaseModel):
    name: str
    description: str | None = None
    active: bool = True


class ProductCategoryUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    active: bool | None = None


class ProductCategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    description: str | None = None
    active: bool
    created_at: datetime
    updated_at: datetime


class ProductBase(BaseModel):
    sku: str
    name: str
    description: str | None = None
    category_id: uuid.UUID | None = None

    length_cm: Decimal | None = None
    width_cm: Decimal | None = None
    height_cm: Decimal | None = None
    weight_kg: Decimal | None = None

    recommended_age_min: int | None = None
    recommended_age_max: int | None = None

    requires_adult_supervision: bool | None = None

    main_material: str | None = None
    paint_type: str | None = None
    finish_type: str | None = None

    non_toxic_paint: bool | None = None
    handmade: bool | None = None

    production_time_hours: Decimal | None = None

    minimum_stock: int = 0
    critical_stock: int = 0

    active: bool = True


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    category_id: uuid.UUID | None = None

    length_cm: Decimal | None = None
    width_cm: Decimal | None = None
    height_cm: Decimal | None = None
    weight_kg: Decimal | None = None

    recommended_age_min: int | None = None
    recommended_age_max: int | None = None

    requires_adult_supervision: bool | None = None

    main_material: str | None = None
    paint_type: str | None = None
    finish_type: str | None = None

    non_toxic_paint: bool | None = None
    handmade: bool | None = None

    production_time_hours: Decimal | None = None

    minimum_stock: int | None = None
    critical_stock: int | None = None

    active: bool | None = None


class ProductImageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    url: str
    position: int
    is_primary: bool
    created_at: datetime


class ProductRead(ProductBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    category: ProductCategoryRead | None = None
    images: list[ProductImageRead] = []
