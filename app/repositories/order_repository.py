from sqlalchemy.orm import Session
from app.models.order import Order


def create_order(db: Session, status: str = "pending") -> Order:
    """Criar um pedido e retornar ele."""
    order = Order(status=status)
    try:
        db.add(order)
        db.commit()
        db.refresh(order)
        return order
    except Exception:
        db.rollback()
        raise
