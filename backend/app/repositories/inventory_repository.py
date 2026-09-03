import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.inventory import Inventory, InventoryMovement


class InventoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def list(
        self,
        product_id: uuid.UUID | None = None,
        warehouse_id: uuid.UUID | None = None,
        low_stock_only: bool = False,
    ) -> list[Inventory]:
        stmt = select(Inventory)
        if product_id is not None:
            stmt = stmt.where(Inventory.product_id == product_id)
        if warehouse_id is not None:
            stmt = stmt.where(Inventory.warehouse_id == warehouse_id)
        if low_stock_only:
            stmt = stmt.where(Inventory.quantity_available <= Inventory.minimum_stock)
        return list(self.db.execute(stmt).scalars().all())

    def get_for_update(
        self, product_id: uuid.UUID, warehouse_id: uuid.UUID
    ) -> Inventory | None:
        """Locks the row (SELECT ... FOR UPDATE) so concurrent movements on the
        same product/warehouse serialize instead of racing on stock_before/after."""
        stmt = (
            select(Inventory)
            .where(Inventory.product_id == product_id, Inventory.warehouse_id == warehouse_id)
            .with_for_update()
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def create(self, inventory: Inventory) -> Inventory:
        self.db.add(inventory)
        self.db.flush()
        return inventory

    def add_movement(self, movement: InventoryMovement) -> InventoryMovement:
        self.db.add(movement)
        self.db.flush()
        return movement

    def list_movements(
        self,
        product_id: uuid.UUID | None = None,
        warehouse_id: uuid.UUID | None = None,
        limit: int = 200,
    ) -> list[InventoryMovement]:
        stmt = select(InventoryMovement).order_by(InventoryMovement.movement_date.desc()).limit(limit)
        if product_id is not None:
            stmt = stmt.where(InventoryMovement.product_id == product_id)
        if warehouse_id is not None:
            stmt = stmt.where(InventoryMovement.warehouse_id == warehouse_id)
        return list(self.db.execute(stmt).scalars().all())
