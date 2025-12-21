# Import all models here so they are registered with Base.metadata
from app.models.product import Product
from app.models.order import Order
from app.models.stock_movement import StockMovement

__all__ = ["Product", "Order", "StockMovement"]
