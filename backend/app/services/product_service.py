import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.product import Product, ProductCategory, ProductImage
from app.repositories.product_repository import (
    ProductCategoryRepository,
    ProductImageRepository,
    ProductRepository,
)
from app.schemas.product import (
    ProductCategoryCreate,
    ProductCategoryUpdate,
    ProductCreate,
    ProductUpdate,
)
from app.services.pdf_export import build_list_pdf

ALLOWED_IMAGE_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
}
MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024


class ProductCategoryService:
    def __init__(self, db: Session):
        self.db = db
        self.categories = ProductCategoryRepository(db)

    def list(self, active_only: bool = False) -> list[ProductCategory]:
        return self.categories.list(active_only=active_only)

    def get(self, category_id: uuid.UUID) -> ProductCategory:
        category = self.categories.get_by_id(category_id)
        if category is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Categoría no encontrada")
        return category

    def create(self, data: ProductCategoryCreate) -> ProductCategory:
        if self.categories.get_by_name(data.name):
            raise HTTPException(status.HTTP_409_CONFLICT, "Ya existe una categoría con ese nombre")
        category = ProductCategory(**data.model_dump())
        self.categories.create(category)
        self.db.commit()
        self.db.refresh(category)
        return category

    def update(self, category_id: uuid.UUID, data: ProductCategoryUpdate) -> ProductCategory:
        category = self.get(category_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(category, field, value)
        self.db.commit()
        self.db.refresh(category)
        return category

    def delete(self, category_id: uuid.UUID) -> None:
        category = self.get(category_id)
        category.active = False
        self.db.commit()

    def export_pdf(self, active_only: bool = False) -> bytes:
        categories = self.list(active_only=active_only)
        rows = [
            [c.name, c.description or "—", "Activa" if c.active else "Inactiva"]
            for c in categories
        ]
        return build_list_pdf("Categorías de productos", ["Nombre", "Descripción", "Estado"], rows)


class ProductService:
    def __init__(self, db: Session):
        self.db = db
        self.products = ProductRepository(db)
        self.categories = ProductCategoryRepository(db)
        self.images = ProductImageRepository(db)

    def list(
        self,
        active_only: bool = False,
        category_id: uuid.UUID | None = None,
        search: str | None = None,
    ) -> list[Product]:
        return self.products.list(active_only=active_only, category_id=category_id, search=search)

    def get(self, product_id: uuid.UUID) -> Product:
        product = self.products.get_by_id(product_id)
        if product is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Producto no encontrado")
        return product

    def create(self, data: ProductCreate) -> Product:
        if self.products.get_by_sku(data.sku):
            raise HTTPException(status.HTTP_409_CONFLICT, "Ya existe un producto con ese SKU")
        if data.category_id is not None and self.categories.get_by_id(data.category_id) is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Categoría no encontrada")

        product = Product(**data.model_dump())
        self.products.create(product)
        self.db.commit()
        self.db.refresh(product)
        return product

    def update(self, product_id: uuid.UUID, data: ProductUpdate) -> Product:
        product = self.get(product_id)
        updates = data.model_dump(exclude_unset=True)

        if "category_id" in updates and updates["category_id"] is not None:
            if self.categories.get_by_id(updates["category_id"]) is None:
                raise HTTPException(status.HTTP_404_NOT_FOUND, "Categoría no encontrada")

        for field, value in updates.items():
            setattr(product, field, value)

        self.db.commit()
        self.db.refresh(product)
        return product

    def add_images(self, product_id: uuid.UUID, files: list[UploadFile]) -> list[ProductImage]:
        product = self.get(product_id)
        if not files:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "No se enviaron archivos")

        upload_dir = Path(get_settings().uploads_dir) / "products" / str(product.id)
        upload_dir.mkdir(parents=True, exist_ok=True)

        existing = self.images.list_by_product(product.id)
        next_position = len(existing)
        has_primary = any(image.is_primary for image in existing)

        created: list[ProductImage] = []
        for file in files:
            if file.content_type not in ALLOWED_IMAGE_TYPES:
                raise HTTPException(
                    status.HTTP_400_BAD_REQUEST, f"Formato no soportado: {file.content_type}"
                )
            contents = file.file.read()
            if len(contents) > MAX_IMAGE_SIZE_BYTES:
                raise HTTPException(
                    status.HTTP_400_BAD_REQUEST, "Cada foto debe pesar menos de 5MB"
                )

            filename = f"{uuid.uuid4()}{ALLOWED_IMAGE_TYPES[file.content_type]}"
            (upload_dir / filename).write_bytes(contents)

            image = ProductImage(
                product_id=product.id,
                filename=filename,
                position=next_position,
                is_primary=not has_primary,
            )
            has_primary = True
            next_position += 1
            self.images.create(image)
            created.append(image)

        self.db.commit()
        for image in created:
            self.db.refresh(image)
        return created

    def delete_image(self, product_id: uuid.UUID, image_id: uuid.UUID) -> None:
        product = self.get(product_id)
        image = self.images.get_by_id(image_id)
        if image is None or image.product_id != product.id:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Foto no encontrada")

        file_path = Path(get_settings().uploads_dir) / "products" / str(product.id) / image.filename
        was_primary = image.is_primary
        self.images.delete(image)
        self.db.commit()
        file_path.unlink(missing_ok=True)

        if was_primary:
            remaining = self.images.list_by_product(product.id)
            if remaining:
                remaining[0].is_primary = True
                self.db.commit()

    def delete(self, product_id: uuid.UUID) -> None:
        product = self.get(product_id)
        product.active = False
        self.db.commit()

    def export_pdf(
        self,
        active_only: bool = False,
        category_id: uuid.UUID | None = None,
        search: str | None = None,
    ) -> bytes:
        products = self.list(active_only=active_only, category_id=category_id, search=search)
        rows = [
            [
                p.sku,
                p.name,
                p.category.name if p.category else "—",
                p.main_material or "—",
                f"{p.minimum_stock} / {p.critical_stock}",
                "Activo" if p.active else "Inactivo",
            ]
            for p in products
        ]
        return build_list_pdf(
            "Productos",
            ["SKU", "Nombre", "Categoría", "Material", "Stock mín. / crít.", "Estado"],
            rows,
        )

    def set_primary_image(self, product_id: uuid.UUID, image_id: uuid.UUID) -> ProductImage:
        product = self.get(product_id)
        image = self.images.get_by_id(image_id)
        if image is None or image.product_id != product.id:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Foto no encontrada")

        self.images.clear_primary(product.id)
        image.is_primary = True
        self.db.commit()
        self.db.refresh(image)
        return image
