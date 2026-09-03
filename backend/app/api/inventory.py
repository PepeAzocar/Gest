import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.user import User
from app.schemas.inventory import (
    InventoryAdjustmentCreate,
    InventoryMovementRead,
    InventoryRead,
    InventoryTransferCreate,
)
from app.security.deps import get_current_user, require_roles
from app.services.inventory_service import InventoryService

router = APIRouter(prefix="/api/inventory", tags=["inventory"])


@router.get("", response_model=list[InventoryRead])
def list_inventory(
    product_id: uuid.UUID | None = None,
    warehouse_id: uuid.UUID | None = None,
    low_stock_only: bool = False,
    db: Session = Depends(get_db),
):
    return InventoryService(db).list(
        product_id=product_id, warehouse_id=warehouse_id, low_stock_only=low_stock_only
    )


@router.get("/movements", response_model=list[InventoryMovementRead])
def list_movements(
    product_id: uuid.UUID | None = None,
    warehouse_id: uuid.UUID | None = None,
    limit: int = 200,
    db: Session = Depends(get_db),
):
    return InventoryService(db).list_movements(
        product_id=product_id, warehouse_id=warehouse_id, limit=limit
    )


@router.post(
    "/adjustments",
    response_model=InventoryMovementRead,
    status_code=201,
    dependencies=[Depends(require_roles("ADMIN", "WAREHOUSE", "PRODUCTION"))],
)
def create_adjustment(
    payload: InventoryAdjustmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return InventoryService(db).adjust(payload, created_by=current_user.id)


@router.post(
    "/transfers",
    status_code=201,
    dependencies=[Depends(require_roles("ADMIN", "WAREHOUSE"))],
)
def create_transfer(
    payload: InventoryTransferCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    movement_out, movement_in = InventoryService(db).transfer(payload, created_by=current_user.id)
    return {
        "movement_out": InventoryMovementRead.model_validate(movement_out),
        "movement_in": InventoryMovementRead.model_validate(movement_in),
    }
