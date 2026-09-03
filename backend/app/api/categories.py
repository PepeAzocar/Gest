import uuid

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.product import ProductCategoryCreate, ProductCategoryRead, ProductCategoryUpdate
from app.security.deps import require_roles
from app.services.product_service import ProductCategoryService

router = APIRouter(prefix="/api/categories", tags=["categories"])


@router.get("", response_model=list[ProductCategoryRead])
def list_categories(active_only: bool = False, db: Session = Depends(get_db)):
    return ProductCategoryService(db).list(active_only=active_only)


@router.get("/export/pdf")
def export_categories_pdf(active_only: bool = False, db: Session = Depends(get_db)):
    pdf = ProductCategoryService(db).export_pdf(active_only=active_only)
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=categorias.pdf"},
    )


@router.get("/{category_id}", response_model=ProductCategoryRead)
def get_category(category_id: uuid.UUID, db: Session = Depends(get_db)):
    return ProductCategoryService(db).get(category_id)


@router.post(
    "",
    response_model=ProductCategoryRead,
    status_code=201,
    dependencies=[Depends(require_roles("ADMIN", "WAREHOUSE"))],
)
def create_category(payload: ProductCategoryCreate, db: Session = Depends(get_db)):
    return ProductCategoryService(db).create(payload)


@router.put(
    "/{category_id}",
    response_model=ProductCategoryRead,
    dependencies=[Depends(require_roles("ADMIN", "WAREHOUSE"))],
)
def update_category(category_id: uuid.UUID, payload: ProductCategoryUpdate, db: Session = Depends(get_db)):
    return ProductCategoryService(db).update(category_id, payload)


@router.delete(
    "/{category_id}",
    status_code=204,
    dependencies=[Depends(require_roles("ADMIN", "WAREHOUSE"))],
)
def delete_category(category_id: uuid.UUID, db: Session = Depends(get_db)):
    ProductCategoryService(db).delete(category_id)
