import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.repositories.customer_repository import CustomerRepository
from app.schemas.customer import CustomerCreate, CustomerUpdate
from app.services.pdf_export import build_list_pdf


class CustomerService:
    def __init__(self, db: Session):
        self.db = db
        self.customers = CustomerRepository(db)

    def list(self, active_only: bool = False, search: str | None = None) -> list[Customer]:
        return self.customers.list(active_only=active_only, search=search)

    def get(self, customer_id: uuid.UUID) -> Customer:
        customer = self.customers.get_by_id(customer_id)
        if customer is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Cliente no encontrado")
        return customer

    def create(self, data: CustomerCreate) -> Customer:
        if data.rut and self.customers.get_by_rut(data.rut):
            raise HTTPException(status.HTTP_409_CONFLICT, "Ya existe un cliente con ese RUT")

        payload = data.model_dump()
        payload["customer_type"] = data.customer_type.value
        customer = Customer(**payload)
        self.customers.create(customer)
        self.db.commit()
        self.db.refresh(customer)
        return customer

    def update(self, customer_id: uuid.UUID, data: CustomerUpdate) -> Customer:
        customer = self.get(customer_id)
        updates = data.model_dump(exclude_unset=True)

        if "rut" in updates and updates["rut"]:
            existing = self.customers.get_by_rut(updates["rut"])
            if existing is not None and existing.id != customer.id:
                raise HTTPException(status.HTTP_409_CONFLICT, "Ya existe un cliente con ese RUT")

        if "customer_type" in updates and updates["customer_type"] is not None:
            updates["customer_type"] = updates["customer_type"].value

        for field, value in updates.items():
            setattr(customer, field, value)

        self.db.commit()
        self.db.refresh(customer)
        return customer

    def delete(self, customer_id: uuid.UUID) -> None:
        customer = self.get(customer_id)
        customer.active = False
        self.db.commit()

    def export_pdf(self, active_only: bool = False, search: str | None = None) -> bytes:
        customers = self.list(active_only=active_only, search=search)
        rows = [
            [
                f"{c.first_name} {c.last_name or ''}".strip(),
                "Persona" if c.customer_type == "PERSON" else "Empresa",
                c.rut or "—",
                c.email or "—",
                c.phone or "—",
                "Activo" if c.active else "Inactivo",
            ]
            for c in customers
        ]
        return build_list_pdf(
            "Clientes", ["Nombre", "Tipo", "RUT", "Email", "Teléfono", "Estado"], rows
        )
