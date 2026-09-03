import uuid

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.customer import CustomerCreate, CustomerRead, CustomerUpdate
from app.security.deps import require_roles
from app.services.customer_service import CustomerService

router = APIRouter(prefix="/api/customers", tags=["customers"])


@router.get("", response_model=list[CustomerRead])
def list_customers(active_only: bool = False, search: str | None = None, db: Session = Depends(get_db)):
    return CustomerService(db).list(active_only=active_only, search=search)


@router.get("/export/pdf")
def export_customers_pdf(
    active_only: bool = False, search: str | None = None, db: Session = Depends(get_db)
):
    pdf = CustomerService(db).export_pdf(active_only=active_only, search=search)
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=clientes.pdf"},
    )


@router.get("/{customer_id}", response_model=CustomerRead)
def get_customer(customer_id: uuid.UUID, db: Session = Depends(get_db)):
    return CustomerService(db).get(customer_id)


@router.post(
    "",
    response_model=CustomerRead,
    status_code=201,
    dependencies=[Depends(require_roles("ADMIN", "SALES"))],
)
def create_customer(payload: CustomerCreate, db: Session = Depends(get_db)):
    return CustomerService(db).create(payload)


@router.put(
    "/{customer_id}",
    response_model=CustomerRead,
    dependencies=[Depends(require_roles("ADMIN", "SALES"))],
)
def update_customer(customer_id: uuid.UUID, payload: CustomerUpdate, db: Session = Depends(get_db)):
    return CustomerService(db).update(customer_id, payload)


@router.delete(
    "/{customer_id}",
    status_code=204,
    dependencies=[Depends(require_roles("ADMIN", "SALES"))],
)
def delete_customer(customer_id: uuid.UUID, db: Session = Depends(get_db)):
    CustomerService(db).delete(customer_id)
