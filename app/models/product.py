from sqlalchemy import Column, Integer, String, Float
from app.db.base import Base


class Product(Base):
    __tablename__ = "products"

    product_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    quantity_on_hand = Column(Integer, default=0, nullable=False)
    average_cost = Column(Float, default=0.0, nullable=False)
