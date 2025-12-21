from typing import List
from pydantic import BaseModel, EmailStr, Field


class OrderItem(BaseModel):
    product_id: int = Field(..., description="ID do produto")
    quantity: int = Field(..., gt=0, description="Quantidade do produto no pedido")


class OrderCreate(BaseModel):
    email: EmailStr = Field(..., description="Email do cliente para notificação")
    items: List[OrderItem]


class OrderRead(BaseModel):
    order_id: int = Field(..., description="ID do pedido")
    status: str = Field(..., description="Status do pedido")

    class Config:
        orm_mode = True
