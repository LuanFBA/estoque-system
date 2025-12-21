from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.product import ProductCreate, ProductRead
from app.services.product_service import create_product
from app.db.session import get_db


router = APIRouter(prefix="/products", tags=["products"])


@router.post("/", response_model=ProductRead)
def create(product: ProductCreate, db: Session = Depends(get_db)):
    try:
        created = create_product(db, product)
        return created
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
