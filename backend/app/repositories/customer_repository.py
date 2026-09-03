import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.customer import Customer


class CustomerRepository:
    def __init__(self, db: Session):
        self.db = db

    def list(self, active_only: bool = False, search: str | None = None) -> list[Customer]:
        stmt = select(Customer).order_by(Customer.first_name)
        if active_only:
            stmt = stmt.where(Customer.active.is_(True))
        if search:
            like = f"%{search}%"
            stmt = stmt.where(
                Customer.first_name.ilike(like)
                | Customer.last_name.ilike(like)
                | Customer.rut.ilike(like)
                | Customer.email.ilike(like)
            )
        return list(self.db.execute(stmt).scalars().all())

    def get_by_id(self, customer_id: uuid.UUID) -> Customer | None:
        return self.db.get(Customer, customer_id)

    def get_by_rut(self, rut: str) -> Customer | None:
        stmt = select(Customer).where(Customer.rut == rut)
        return self.db.execute(stmt).scalar_one_or_none()

    def create(self, customer: Customer) -> Customer:
        self.db.add(customer)
        self.db.flush()
        return customer
