from sqlalchemy.orm import Session
from app.repositories import product_repository
from app.schemas.product import ProductCreate


def create_product(db: Session, product_in: ProductCreate):
    return product_repository.create_product(
        db,
        name=product_in.name,
        quantity_on_hand=product_in.quantity_on_hand,
        average_cost=product_in.average_cost,
    )
