import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class WarehouseCreate(BaseModel):
    code: str
    name: str
    description: str | None = None
    active: bool = True


class WarehouseUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    active: bool | None = None


class WarehouseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    code: str
    name: str
    description: str | None = None
    active: bool
    created_at: datetime
