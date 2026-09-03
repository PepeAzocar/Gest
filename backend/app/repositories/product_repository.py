import uuid

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models.product import Product, ProductCategory, ProductImage


class ProductCategoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def list(self, active_only: bool = False) -> list[ProductCategory]:
        stmt = select(ProductCategory).order_by(ProductCategory.name)
        if active_only:
            stmt = stmt.where(ProductCategory.active.is_(True))
        return list(self.db.execute(stmt).scalars().all())

    def get_by_id(self, category_id: uuid.UUID) -> ProductCategory | None:
        return self.db.get(ProductCategory, category_id)

    def get_by_name(self, name: str) -> ProductCategory | None:
        stmt = select(ProductCategory).where(ProductCategory.name == name)
        return self.db.execute(stmt).scalar_one_or_none()

    def create(self, category: ProductCategory) -> ProductCategory:
        self.db.add(category)
        self.db.flush()
        return category


class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    def list(
        self,
        active_only: bool = False,
        category_id: uuid.UUID | None = None,
        search: str | None = None,
    ) -> list[Product]:
        stmt = select(Product).order_by(Product.name)
        if active_only:
            stmt = stmt.where(Product.active.is_(True))
        if category_id is not None:
            stmt = stmt.where(Product.category_id == category_id)
        if search:
            like = f"%{search}%"
            stmt = stmt.where(Product.name.ilike(like) | Product.sku.ilike(like))
        return list(self.db.execute(stmt).scalars().all())

    def get_by_id(self, product_id: uuid.UUID) -> Product | None:
        return self.db.get(Product, product_id)

    def get_by_sku(self, sku: str) -> Product | None:
        stmt = select(Product).where(Product.sku == sku)
        return self.db.execute(stmt).scalar_one_or_none()

    def create(self, product: Product) -> Product:
        self.db.add(product)
        self.db.flush()
        return product


class ProductImageRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_by_product(self, product_id: uuid.UUID) -> list[ProductImage]:
        stmt = (
            select(ProductImage)
            .where(ProductImage.product_id == product_id)
            .order_by(ProductImage.position)
        )
        return list(self.db.execute(stmt).scalars().all())

    def get_by_id(self, image_id: uuid.UUID) -> ProductImage | None:
        return self.db.get(ProductImage, image_id)

    def create(self, image: ProductImage) -> ProductImage:
        self.db.add(image)
        self.db.flush()
        return image

    def delete(self, image: ProductImage) -> None:
        self.db.delete(image)

    def clear_primary(self, product_id: uuid.UUID) -> None:
        stmt = (
            update(ProductImage)
            .where(ProductImage.product_id == product_id)
            .values(is_primary=False)
        )
        self.db.execute(stmt)
