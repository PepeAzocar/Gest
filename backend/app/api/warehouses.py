import uuid

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.warehouse import WarehouseCreate, WarehouseRead, WarehouseUpdate
from app.security.deps import require_roles
from app.services.inventory_service import WarehouseService

router = APIRouter(prefix="/api/warehouses", tags=["warehouses"])


@router.get("", response_model=list[WarehouseRead])
def list_warehouses(active_only: bool = False, db: Session = Depends(get_db)):
    return WarehouseService(db).list(active_only=active_only)


@router.get("/export/pdf")
def export_warehouses_pdf(active_only: bool = False, db: Session = Depends(get_db)):
    pdf = WarehouseService(db).export_pdf(active_only=active_only)
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=bodegas.pdf"},
    )


@router.get("/{warehouse_id}", response_model=WarehouseRead)
def get_warehouse(warehouse_id: uuid.UUID, db: Session = Depends(get_db)):
    return WarehouseService(db).get(warehouse_id)


@router.post(
    "",
    response_model=WarehouseRead,
    status_code=201,
    dependencies=[Depends(require_roles("ADMIN", "WAREHOUSE"))],
)
def create_warehouse(payload: WarehouseCreate, db: Session = Depends(get_db)):
    return WarehouseService(db).create(payload)


@router.put(
    "/{warehouse_id}",
    response_model=WarehouseRead,
    dependencies=[Depends(require_roles("ADMIN", "WAREHOUSE"))],
)
def update_warehouse(warehouse_id: uuid.UUID, payload: WarehouseUpdate, db: Session = Depends(get_db)):
    return WarehouseService(db).update(warehouse_id, payload)


@router.delete(
    "/{warehouse_id}",
    status_code=204,
    dependencies=[Depends(require_roles("ADMIN", "WAREHOUSE"))],
)
def delete_warehouse(warehouse_id: uuid.UUID, db: Session = Depends(get_db)):
    WarehouseService(db).delete(warehouse_id)
