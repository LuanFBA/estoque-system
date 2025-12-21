"""
Testes unitários para os schemas Pydantic.
"""

import pytest
from pydantic import ValidationError
from app.schemas.order import OrderCreate, OrderRead, OrderItem
from app.schemas.product import ProductCreate, ProductRead


class TestOrderItem:
    """Testes para OrderItem schema."""

    def test_valid_order_item(self):
        """Deve criar OrderItem válido."""
        item = OrderItem(product_id=1, quantity=5)

        assert item.product_id == 1
        assert item.quantity == 5

    def test_order_item_quantity_must_be_positive(self):
        """Deve rejeitar quantity <= 0."""
        with pytest.raises(ValidationError):
            OrderItem(product_id=1, quantity=0)

        with pytest.raises(ValidationError):
            OrderItem(product_id=1, quantity=-1)

    def test_order_item_requires_product_id(self):
        """Deve exigir product_id."""
        with pytest.raises(ValidationError):
            OrderItem(quantity=5)


class TestOrderCreate:
    """Testes para OrderCreate schema."""

    def test_valid_order_create(self):
        """Deve criar OrderCreate válido."""
        order = OrderCreate(
            email="cliente@teste.com", items=[{"product_id": 1, "quantity": 2}]
        )

        assert order.email == "cliente@teste.com"
        assert len(order.items) == 1
        assert order.items[0].product_id == 1

    def test_order_create_requires_valid_email(self):
        """Deve exigir email válido."""
        with pytest.raises(ValidationError):
            OrderCreate(
                email="email-invalido", items=[{"product_id": 1, "quantity": 1}]
            )

    def test_order_create_requires_items(self):
        """Deve exigir items."""
        with pytest.raises(ValidationError):
            OrderCreate(email="test@test.com")

    def test_order_create_with_multiple_items(self):
        """Deve aceitar múltiplos items."""
        order = OrderCreate(
            email="cliente@teste.com",
            items=[
                {"product_id": 1, "quantity": 2},
                {"product_id": 2, "quantity": 3},
                {"product_id": 3, "quantity": 1},
            ],
        )

        assert len(order.items) == 3


class TestOrderRead:
    """Testes para OrderRead schema."""

    def test_order_read_from_orm(self):
        """Deve criar OrderRead a partir de ORM."""

        class MockOrder:
            order_id = 123
            status = "pending"

        order = OrderRead.from_orm(MockOrder())

        assert order.order_id == 123
        assert order.status == "pending"


class TestProductCreate:
    """Testes para ProductCreate schema."""

    def test_valid_product_create(self):
        """Deve criar ProductCreate válido."""
        product = ProductCreate(name="Caneta", quantity_on_hand=100, average_cost=2.50)

        assert product.name == "Caneta"
        assert product.quantity_on_hand == 100
        assert product.average_cost == 2.50

    def test_product_create_with_defaults(self):
        """Deve usar valores padrão."""
        product = ProductCreate(name="Lápis")

        assert product.name == "Lápis"
        assert product.quantity_on_hand == 0
        assert product.average_cost == 0.0

    def test_product_create_requires_name(self):
        """Deve exigir name."""
        with pytest.raises(ValidationError):
            ProductCreate(quantity_on_hand=10)


class TestProductRead:
    """Testes para ProductRead schema."""

    def test_product_read_from_orm(self):
        """Deve criar ProductRead a partir de ORM."""

        class MockProduct:
            product_id = 1
            name = "Produto"
            quantity_on_hand = 50
            average_cost = 10.0

        product = ProductRead.from_orm(MockProduct())

        assert product.product_id == 1
        assert product.name == "Produto"
        assert product.quantity_on_hand == 50
        assert product.average_cost == 10.0
