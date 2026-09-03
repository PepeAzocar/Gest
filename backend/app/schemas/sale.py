import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.sale import PaymentStatus, SalesChannel
from app.schemas.customer import CustomerRead
from app.schemas.product import ProductRead
from app.schemas.warehouse import WarehouseRead


class SaleItemCreate(BaseModel):
    product_id: uuid.UUID
    quantity: Decimal = Field(gt=0)
    unit_price: Decimal = Field(ge=0)
    discount_amount: Decimal = Field(default=Decimal("0"), ge=0)


class SaleItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    product_id: uuid.UUID
    quantity: Decimal
    unit_price: Decimal
    discount_amount: Decimal
    subtotal: Decimal
    product_cost: Decimal | None = None
    margin: Decimal | None = None
    product: ProductRead | None = None


class SaleCreate(BaseModel):
    customer_id: uuid.UUID | None = None
    warehouse_id: uuid.UUID
    sales_channel: SalesChannel
    payment_method: str | None = None
    payment_status: PaymentStatus = PaymentStatus.PENDING
    discount_amount: Decimal = Field(default=Decimal("0"), ge=0)
    tax_amount: Decimal = Field(default=Decimal("0"), ge=0)
    notes: str | None = None
    items: list[SaleItemCreate] = Field(min_length=1)


class SaleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    sale_number: str
    customer_id: uuid.UUID | None = None
    warehouse_id: uuid.UUID
    sale_date: datetime
    status: str
    subtotal: Decimal
    discount_amount: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    payment_status: str
    payment_method: str | None = None
    sales_channel: str
    notes: str | None = None
    created_at: datetime
    updated_at: datetime
    items: list[SaleItemRead] = []
    customer: CustomerRead | None = None
    warehouse: WarehouseRead | None = None
