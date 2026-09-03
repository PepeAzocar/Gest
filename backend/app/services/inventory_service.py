import uuid
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.inventory import (
    DECREASES_ON_HAND,
    INCREASES_ON_HAND,
    MANUAL_ADJUSTMENT_TYPES,
    Inventory,
    InventoryMovement,
    MovementType,
)
from app.repositories.inventory_repository import InventoryRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.warehouse_repository import WarehouseRepository
from app.schemas.inventory import InventoryAdjustmentCreate, InventoryTransferCreate
from app.schemas.warehouse import WarehouseCreate, WarehouseUpdate
from app.models.warehouse import Warehouse
from app.services.pdf_export import build_list_pdf


class WarehouseService:
    def __init__(self, db: Session):
        self.db = db
        self.warehouses = WarehouseRepository(db)

    def list(self, active_only: bool = False):
        return self.warehouses.list(active_only=active_only)

    def get(self, warehouse_id: uuid.UUID):
        warehouse = self.warehouses.get_by_id(warehouse_id)
        if warehouse is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Bodega no encontrada")
        return warehouse

    def create(self, data: WarehouseCreate):
        if self.warehouses.get_by_code(data.code):
            raise HTTPException(status.HTTP_409_CONFLICT, "Ya existe una bodega con ese código")

        warehouse = Warehouse(**data.model_dump())
        self.warehouses.create(warehouse)
        self.db.commit()
        self.db.refresh(warehouse)
        return warehouse

    def update(self, warehouse_id: uuid.UUID, data: WarehouseUpdate):
        warehouse = self.get(warehouse_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(warehouse, field, value)
        self.db.commit()
        self.db.refresh(warehouse)
        return warehouse

    def delete(self, warehouse_id: uuid.UUID) -> None:
        warehouse = self.get(warehouse_id)
        warehouse.active = False
        self.db.commit()

    def export_pdf(self, active_only: bool = False) -> bytes:
        warehouses = self.list(active_only=active_only)
        rows = [
            [w.code, w.name, w.description or "—", "Activa" if w.active else "Inactiva"]
            for w in warehouses
        ]
        return build_list_pdf("Bodegas", ["Código", "Nombre", "Descripción", "Estado"], rows)


class InventoryService:
    """Owns the one rule that matters: quantity_on_hand only ever changes as the
    side effect of an InventoryMovement, inside a single DB transaction."""

    def __init__(self, db: Session):
        self.db = db
        self.inventory = InventoryRepository(db)
        self.products = ProductRepository(db)
        self.warehouses = WarehouseRepository(db)

    def list(
        self,
        product_id: uuid.UUID | None = None,
        warehouse_id: uuid.UUID | None = None,
        low_stock_only: bool = False,
    ) -> list[Inventory]:
        return self.inventory.list(
            product_id=product_id, warehouse_id=warehouse_id, low_stock_only=low_stock_only
        )

    def list_movements(
        self,
        product_id: uuid.UUID | None = None,
        warehouse_id: uuid.UUID | None = None,
        limit: int = 200,
    ) -> list[InventoryMovement]:
        return self.inventory.list_movements(
            product_id=product_id, warehouse_id=warehouse_id, limit=limit
        )

    def _get_or_create_locked(self, product_id: uuid.UUID, warehouse_id: uuid.UUID) -> Inventory:
        inv = self.inventory.get_for_update(product_id, warehouse_id)
        if inv is not None:
            return inv

        # First movement ever for this product/warehouse: create the row, then
        # re-select it under the lock so concurrent callers serialize on it too.
        inv = Inventory(product_id=product_id, warehouse_id=warehouse_id)
        self.inventory.create(inv)
        return self.inventory.get_for_update(product_id, warehouse_id)

    def apply_movement(
        self,
        product_id: uuid.UUID,
        warehouse_id: uuid.UUID,
        movement_type: MovementType,
        quantity: Decimal,
        reason: str | None,
        reference_type: str | None = None,
        reference_id: uuid.UUID | None = None,
        created_by: uuid.UUID | None = None,
    ) -> InventoryMovement:
        if quantity <= 0:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "La cantidad debe ser mayor a cero")
        if self.products.get_by_id(product_id) is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Producto no encontrado")
        if self.warehouses.get_by_id(warehouse_id) is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Bodega no encontrada")

        inv = self._get_or_create_locked(product_id, warehouse_id)

        stock_before = inv.quantity_on_hand
        if movement_type in INCREASES_ON_HAND:
            stock_after = stock_before + quantity
        elif movement_type in DECREASES_ON_HAND:
            stock_after = stock_before - quantity
            if stock_after < 0:
                raise HTTPException(
                    status.HTTP_409_CONFLICT,
                    f"Stock insuficiente. Disponible: {stock_before} Solicitado: {quantity}",
                )
        else:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                f"Tipo de movimiento no soportado para ajustar quantity_on_hand: {movement_type}",
            )

        inv.quantity_on_hand = stock_after

        movement = InventoryMovement(
            product_id=product_id,
            warehouse_id=warehouse_id,
            movement_type=movement_type.value,
            quantity=quantity,
            stock_before=stock_before,
            stock_after=stock_after,
            reference_type=reference_type,
            reference_id=reference_id,
            reason=reason,
            created_by=created_by,
        )
        self.inventory.add_movement(movement)
        return movement

    def adjust(
        self, data: InventoryAdjustmentCreate, created_by: uuid.UUID | None
    ) -> InventoryMovement:
        if data.movement_type not in MANUAL_ADJUSTMENT_TYPES:
            allowed = ", ".join(t.value for t in MANUAL_ADJUSTMENT_TYPES)
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                f"Tipo de movimiento no permitido en ajustes manuales. Usa uno de: {allowed}",
            )
        movement = self.apply_movement(
            product_id=data.product_id,
            warehouse_id=data.warehouse_id,
            movement_type=data.movement_type,
            quantity=data.quantity,
            reason=data.reason,
            reference_type="ADJUSTMENT",
            created_by=created_by,
        )
        self.db.commit()
        self.db.refresh(movement)
        return movement

    def transfer(
        self, data: InventoryTransferCreate, created_by: uuid.UUID | None
    ) -> tuple[InventoryMovement, InventoryMovement]:
        if data.source_warehouse_id == data.destination_warehouse_id:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, "La bodega de origen y destino no pueden ser la misma"
            )

        transfer_id = uuid.uuid4()

        movement_out = self.apply_movement(
            product_id=data.product_id,
            warehouse_id=data.source_warehouse_id,
            movement_type=MovementType.TRANSFER_OUT,
            quantity=data.quantity,
            reason=data.reason,
            reference_type="TRANSFER",
            reference_id=transfer_id,
            created_by=created_by,
        )
        movement_in = self.apply_movement(
            product_id=data.product_id,
            warehouse_id=data.destination_warehouse_id,
            movement_type=MovementType.TRANSFER_IN,
            quantity=data.quantity,
            reason=data.reason,
            reference_type="TRANSFER",
            reference_id=transfer_id,
            created_by=created_by,
        )

        self.db.commit()
        self.db.refresh(movement_out)
        self.db.refresh(movement_in)
        return movement_out, movement_in
