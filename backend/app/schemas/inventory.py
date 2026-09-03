import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.inventory import MovementType
from app.schemas.product import ProductRead
from app.schemas.warehouse import WarehouseRead


class InventoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    product_id: uuid.UUID
    warehouse_id: uuid.UUID
    quantity_on_hand: Decimal
    quantity_reserved: Decimal
    quantity_available: Decimal
    minimum_stock: int
    critical_stock: int
    updated_at: datetime
    product: ProductRead | None = None
    warehouse: WarehouseRead | None = None


class InventoryMovementRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    product_id: uuid.UUID
    warehouse_id: uuid.UUID
    movement_type: str
    quantity: Decimal
    stock_before: Decimal
    stock_after: Decimal
    reference_type: str | None = None
    reference_id: uuid.UUID | None = None
    reason: str | None = None
    movement_date: datetime
    created_by: uuid.UUID | None = None
    created_at: datetime


class InventoryAdjustmentCreate(BaseModel):
    product_id: uuid.UUID
    warehouse_id: uuid.UUID
    movement_type: MovementType
    quantity: Decimal = Field(gt=0)
    reason: str


class InventoryTransferCreate(BaseModel):
    product_id: uuid.UUID
    source_warehouse_id: uuid.UUID
    destination_warehouse_id: uuid.UUID
    quantity: Decimal = Field(gt=0)
    reason: str
