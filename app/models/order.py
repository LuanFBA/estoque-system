from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from app.db.base import Base


class Order(Base):
    __tablename__ = "orders"

    order_id = Column(Integer, primary_key=True, index=True)
    status = Column(String, default="pending", nullable=False)
    created_at = Column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
