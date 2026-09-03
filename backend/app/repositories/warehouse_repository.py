import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.warehouse import Warehouse


class WarehouseRepository:
    def __init__(self, db: Session):
        self.db = db

    def list(self, active_only: bool = False) -> list[Warehouse]:
        stmt = select(Warehouse).order_by(Warehouse.name)
        if active_only:
            stmt = stmt.where(Warehouse.active.is_(True))
        return list(self.db.execute(stmt).scalars().all())

    def get_by_id(self, warehouse_id: uuid.UUID) -> Warehouse | None:
        return self.db.get(Warehouse, warehouse_id)

    def get_by_code(self, code: str) -> Warehouse | None:
        stmt = select(Warehouse).where(Warehouse.code == code)
        return self.db.execute(stmt).scalar_one_or_none()

    def create(self, warehouse: Warehouse) -> Warehouse:
        self.db.add(warehouse)
        self.db.flush()
        return warehouse
