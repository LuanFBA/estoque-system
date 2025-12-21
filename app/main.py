from fastapi import FastAPI
from app.api.routes import orders, products


app = FastAPI(title="Sistema de Estoque Assíncrono")
app.include_router(orders.router)
app.include_router(products.router)
