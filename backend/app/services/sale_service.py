import uuid
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.inventory import MovementType
from app.models.sale import PaymentStatus, Sale, SaleItem, SaleStatus
from app.repositories.customer_repository import CustomerRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.sale_repository import SaleRepository
from app.repositories.warehouse_repository import WarehouseRepository
from app.schemas.sale import SaleCreate
from app.services.inventory_service import InventoryService


class SaleService:
    def __init__(self, db: Session):
        self.db = db
        self.sales = SaleRepository(db)
        self.customers = CustomerRepository(db)
        self.warehouses = WarehouseRepository(db)
        self.products = ProductRepository(db)
        self.inventory_service = InventoryService(db)

    def list(
        self,
        status_: str | None = None,
        customer_id: uuid.UUID | None = None,
        sales_channel: str | None = None,
        limit: int = 200,
    ) -> list[Sale]:
        return self.sales.list(
            status=status_, customer_id=customer_id, sales_channel=sales_channel, limit=limit
        )

    def get(self, sale_id: uuid.UUID) -> Sale:
        sale = self.sales.get_by_id(sale_id)
        if sale is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Venta no encontrada")
        return sale

    def create(self, data: SaleCreate, created_by: uuid.UUID | None) -> Sale:
        if self.warehouses.get_by_id(data.warehouse_id) is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Bodega no encontrada")
        if data.customer_id is not None and self.customers.get_by_id(data.customer_id) is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Cliente no encontrado")

        sale_status = (
            SaleStatus.PAID.value
            if data.payment_status == PaymentStatus.PAID
            else SaleStatus.PENDING_PAYMENT.value
        )

        sale = Sale(
            sale_number=self.sales.next_sale_number(),
            customer_id=data.customer_id,
            warehouse_id=data.warehouse_id,
            status=sale_status,
            payment_status=data.payment_status.value,
            payment_method=data.payment_method,
            sales_channel=data.sales_channel.value,
            notes=data.notes,
            created_by=created_by,
        )
        self.sales.create(sale)

        items_subtotal = Decimal("0")
        for item_data in data.items:
            product = self.products.get_by_id(item_data.product_id)
            if product is None:
                raise HTTPException(
                    status.HTTP_404_NOT_FOUND, f"Producto no encontrado: {item_data.product_id}"
                )

            item_subtotal = item_data.quantity * item_data.unit_price - item_data.discount_amount
            self.db.add(
                SaleItem(
                    sale_id=sale.id,
                    product_id=item_data.product_id,
                    quantity=item_data.quantity,
                    unit_price=item_data.unit_price,
                    discount_amount=item_data.discount_amount,
                    subtotal=item_subtotal,
                )
            )
            items_subtotal += item_subtotal

            # Raises (409 insufficient stock / 404) and the whole transaction rolls
            # back with it — a sale is never left half-registered against stock.
            self.inventory_service.apply_movement(
                product_id=item_data.product_id,
                warehouse_id=data.warehouse_id,
                movement_type=MovementType.SALE,
                quantity=item_data.quantity,
                reason=f"Venta {sale.sale_number}",
                reference_type="SALE",
                reference_id=sale.id,
                created_by=created_by,
            )

        sale.subtotal = items_subtotal
        sale.discount_amount = data.discount_amount
        sale.tax_amount = data.tax_amount
        sale.total_amount = items_subtotal - data.discount_amount + data.tax_amount

        self.db.commit()
        self.db.refresh(sale)
        return sale

    def cancel(self, sale_id: uuid.UUID, cancelled_by: uuid.UUID | None) -> Sale:
        sale = self.get(sale_id)
        if sale.status in (SaleStatus.CANCELLED.value, SaleStatus.REFUNDED.value):
            raise HTTPException(status.HTTP_409_CONFLICT, "La venta ya está cancelada o reembolsada")

        for item in sale.items:
            self.inventory_service.apply_movement(
                product_id=item.product_id,
                warehouse_id=sale.warehouse_id,
                movement_type=MovementType.SALE_CANCEL,
                quantity=item.quantity,
                reason=f"Cancelación venta {sale.sale_number}",
                reference_type="SALE",
                reference_id=sale.id,
                created_by=cancelled_by,
            )

        sale.status = SaleStatus.CANCELLED.value
        if sale.payment_status == PaymentStatus.PAID.value:
            sale.payment_status = PaymentStatus.REFUNDED.value

        self.db.commit()
        self.db.refresh(sale)
        return sale
