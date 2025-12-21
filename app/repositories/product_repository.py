from sqlalchemy.orm import Session
from app.models.product import Product


def create_product(
    db: Session, name: str, quantity_on_hand: int = 0, average_cost: float = 0.0
) -> Product:
    product = Product(
        name=name, quantity_on_hand=quantity_on_hand, average_cost=average_cost
    )
    try:
        db.add(product)
        db.commit()
        db.refresh(product)
        return product
    except Exception:
        db.rollback()
        raise
