from pydantic import BaseModel


class ProductCreate(BaseModel):
    name: str
    quantity_on_hand: int = 0
    average_cost: float = 0.0


class ProductRead(ProductCreate):
    product_id: int

    class Config:
        orm_mode = True
