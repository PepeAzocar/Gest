import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict


class CustomerType(str, Enum):
    PERSON = "PERSON"
    COMPANY = "COMPANY"


class CustomerCreate(BaseModel):
    customer_type: CustomerType = CustomerType.PERSON
    first_name: str
    last_name: str | None = None
    rut: str | None = None
    email: str | None = None
    phone: str | None = None
    address: str | None = None
    commune: str | None = None
    region: str | None = None
    notes: str | None = None
    active: bool = True


class CustomerUpdate(BaseModel):
    customer_type: CustomerType | None = None
    first_name: str | None = None
    last_name: str | None = None
    rut: str | None = None
    email: str | None = None
    phone: str | None = None
    address: str | None = None
    commune: str | None = None
    region: str | None = None
    notes: str | None = None
    active: bool | None = None


class CustomerRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    customer_type: str
    first_name: str
    last_name: str | None = None
    rut: str | None = None
    email: str | None = None
    phone: str | None = None
    address: str | None = None
    commune: str | None = None
    region: str | None = None
    notes: str | None = None
    active: bool
    created_at: datetime
    updated_at: datetime
