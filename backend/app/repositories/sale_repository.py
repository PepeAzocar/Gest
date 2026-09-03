import uuid

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.models.sale import Sale


class SaleRepository:
    def __init__(self, db: Session):
        self.db = db

    def next_sale_number(self) -> str:
        seq_value = self.db.execute(text("SELECT nextval('sale_number_seq')")).scalar_one()
        return f"V-{seq_value:06d}"

    def list(
        self,
        status: str | None = None,
        customer_id: uuid.UUID | None = None,
        sales_channel: str | None = None,
        limit: int = 200,
    ) -> list[Sale]:
        stmt = select(Sale).order_by(Sale.sale_date.desc()).limit(limit)
        if status is not None:
            stmt = stmt.where(Sale.status == status)
        if customer_id is not None:
            stmt = stmt.where(Sale.customer_id == customer_id)
        if sales_channel is not None:
            stmt = stmt.where(Sale.sales_channel == sales_channel)
        return list(self.db.execute(stmt).scalars().all())

    def get_by_id(self, sale_id: uuid.UUID) -> Sale | None:
        return self.db.get(Sale, sale_id)

    def create(self, sale: Sale) -> Sale:
        self.db.add(sale)
        self.db.flush()
        return sale
