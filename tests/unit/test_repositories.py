"""
Testes unitários para os repositories.
"""

import pytest
from app.repositories.order_repository import create_order
from app.repositories.product_repository import create_product
from app.models.order import Order
from app.models.product import Product


class TestOrderRepository:
    """Testes para order_repository."""

    def test_create_order_with_default_status(self, db_session):
        """Deve criar um pedido com status 'pending' por padrão."""
        order = create_order(db_session)

        assert order is not None
        assert order.order_id is not None
        assert order.status == "pending"

    def test_create_order_with_custom_status(self, db_session):
        """Deve criar um pedido com status personalizado."""
        order = create_order(db_session, status="confirmed")

        assert order.status == "confirmed"

    def test_create_order_persists_to_database(self, db_session):
        """Deve persistir o pedido no banco de dados."""
        order = create_order(db_session)

        # Buscar o pedido do banco
        db_order = (
            db_session.query(Order).filter(Order.order_id == order.order_id).first()
        )

        assert db_order is not None
        assert db_order.order_id == order.order_id
        assert db_order.status == order.status

    def test_create_multiple_orders(self, db_session):
        """Deve criar múltiplos pedidos com IDs diferentes."""
        order1 = create_order(db_session)
        order2 = create_order(db_session)
        order3 = create_order(db_session)

        assert order1.order_id != order2.order_id
        assert order2.order_id != order3.order_id


class TestProductRepository:
    """Testes para product_repository."""

    def test_create_product_with_all_fields(self, db_session):
        """Deve criar um produto com todos os campos."""
        product = create_product(
            db_session, name="Caneta Azul", quantity_on_hand=100, average_cost=2.50
        )

        assert product is not None
        assert product.product_id is not None
        assert product.name == "Caneta Azul"
        assert product.quantity_on_hand == 100
        assert product.average_cost == 2.50

    def test_create_product_with_defaults(self, db_session):
        """Deve criar um produto com valores padrão."""
        product = create_product(db_session, name="Produto Simples")

        assert product.name == "Produto Simples"
        assert product.quantity_on_hand == 0
        assert product.average_cost == 0.0

    def test_create_product_persists_to_database(self, db_session):
        """Deve persistir o produto no banco de dados."""
        product = create_product(db_session, name="Lápis")

        db_product = (
            db_session.query(Product)
            .filter(Product.product_id == product.product_id)
            .first()
        )

        assert db_product is not None
        assert db_product.name == "Lápis"

    def test_create_multiple_products(self, db_session):
        """Deve criar múltiplos produtos."""
        p1 = create_product(db_session, name="Produto 1")
        p2 = create_product(db_session, name="Produto 2")

        assert p1.product_id != p2.product_id
        assert p1.name != p2.name
