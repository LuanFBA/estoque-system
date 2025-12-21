from sqlalchemy.orm import Session
from app.core.rabbitmq import publish_event
from app.repositories import order_repository


def create_order(db: Session, items: list[dict], email: str):
    """Criar um pedido e publicar o evento.
    """
    order = order_repository.create_order(db, status="pending")

    payload = {
        "order_id": order.order_id,
        "email": email,
        "items": items,
    }

    publish_event("order.created", payload)
    return order
