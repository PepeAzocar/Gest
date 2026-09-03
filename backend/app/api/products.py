import uuid

from fastapi import APIRouter, Depends, File, Response, UploadFile
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.product import ProductCreate, ProductImageRead, ProductRead, ProductUpdate
from app.security.deps import require_roles
from app.services.product_service import ProductService

router = APIRouter(prefix="/api/products", tags=["products"])


@router.get("", response_model=list[ProductRead])
def list_products(
    active_only: bool = False,
    category_id: uuid.UUID | None = None,
    search: str | None = None,
    db: Session = Depends(get_db),
):
    return ProductService(db).list(active_only=active_only, category_id=category_id, search=search)


@router.get("/export/pdf")
def export_products_pdf(
    active_only: bool = False,
    category_id: uuid.UUID | None = None,
    search: str | None = None,
    db: Session = Depends(get_db),
):
    pdf = ProductService(db).export_pdf(active_only=active_only, category_id=category_id, search=search)
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=productos.pdf"},
    )


@router.get("/{product_id}", response_model=ProductRead)
def get_product(product_id: uuid.UUID, db: Session = Depends(get_db)):
    return ProductService(db).get(product_id)


@router.post(
    "",
    response_model=ProductRead,
    status_code=201,
    dependencies=[Depends(require_roles("ADMIN", "WAREHOUSE"))],
)
def create_product(payload: ProductCreate, db: Session = Depends(get_db)):
    return ProductService(db).create(payload)


@router.put(
    "/{product_id}",
    response_model=ProductRead,
    dependencies=[Depends(require_roles("ADMIN", "WAREHOUSE"))],
)
def update_product(product_id: uuid.UUID, payload: ProductUpdate, db: Session = Depends(get_db)):
    return ProductService(db).update(product_id, payload)


@router.delete(
    "/{product_id}",
    status_code=204,
    dependencies=[Depends(require_roles("ADMIN", "WAREHOUSE"))],
)
def delete_product(product_id: uuid.UUID, db: Session = Depends(get_db)):
    ProductService(db).delete(product_id)


@router.post(
    "/{product_id}/images",
    response_model=list[ProductImageRead],
    status_code=201,
    dependencies=[Depends(require_roles("ADMIN", "WAREHOUSE"))],
)
def upload_product_images(
    product_id: uuid.UUID,
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
):
    return ProductService(db).add_images(product_id, files)


@router.delete(
    "/{product_id}/images/{image_id}",
    status_code=204,
    dependencies=[Depends(require_roles("ADMIN", "WAREHOUSE"))],
)
def delete_product_image(product_id: uuid.UUID, image_id: uuid.UUID, db: Session = Depends(get_db)):
    ProductService(db).delete_image(product_id, image_id)


@router.put(
    "/{product_id}/images/{image_id}/primary",
    response_model=ProductImageRead,
    dependencies=[Depends(require_roles("ADMIN", "WAREHOUSE"))],
)
def set_primary_product_image(
    product_id: uuid.UUID, image_id: uuid.UUID, db: Session = Depends(get_db)
):
    return ProductService(db).set_primary_image(product_id, image_id)
