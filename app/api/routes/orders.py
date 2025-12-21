from typing import List

import logging
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from app.schemas.order import OrderCreate, OrderRead
from app.services.order_service import create_order
from app.db.session import get_db

logger = logging.getLogger(__name__)


router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
def create_order_endpoint(order: OrderCreate, db: Session = Depends(get_db)):
    try:
        items: List[dict] = [item.dict() for item in order.items]
        created = create_order(db, items, order.email)
        return created
    except Exception as exc:
        logger.exception("Erro ao criar pedido: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc
