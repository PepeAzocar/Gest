import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.user import User
from app.schemas.sale import SaleCreate, SaleRead
from app.security.deps import get_current_user, require_roles
from app.services.sale_service import SaleService

router = APIRouter(prefix="/api/sales", tags=["sales"])


@router.get("", response_model=list[SaleRead])
def list_sales(
    status: str | None = None,
    customer_id: uuid.UUID | None = None,
    sales_channel: str | None = None,
    db: Session = Depends(get_db),
):
    return SaleService(db).list(status_=status, customer_id=customer_id, sales_channel=sales_channel)


@router.get("/{sale_id}", response_model=SaleRead)
def get_sale(sale_id: uuid.UUID, db: Session = Depends(get_db)):
    return SaleService(db).get(sale_id)


@router.post(
    "",
    response_model=SaleRead,
    status_code=201,
    dependencies=[Depends(require_roles("ADMIN", "SALES"))],
)
def create_sale(
    payload: SaleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return SaleService(db).create(payload, created_by=current_user.id)


@router.post(
    "/{sale_id}/cancel",
    response_model=SaleRead,
    dependencies=[Depends(require_roles("ADMIN", "SALES"))],
)
def cancel_sale(
    sale_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return SaleService(db).cancel(sale_id, cancelled_by=current_user.id)
