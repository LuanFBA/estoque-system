"""
Testes unitários para os services.
"""

import pytest
from unittest.mock import patch, MagicMock
from app.services.order_service import create_order
from app.services.product_service import create_product
from app.services.stock_service import reserve_stock
from app.services.payment_service import process_payment
from app.services.email_service import (
    send_email,
    send_order_processed_email,
    send_payment_failed_email,
)
from app.models.product import Product
from app.repositories.product_repository import create_product as repo_create_product


class TestOrderService:
    """Testes para order_service."""

    @patch("app.services.order_service.publish_event")
    def test_create_order_publishes_event(self, mock_publish, db_session):
        """Deve criar pedido e publicar evento order.created."""
        items = [{"product_id": 1, "quantity": 2}]
        email = "cliente@teste.com"

        order = create_order(db_session, items, email)

        assert order is not None
        assert order.order_id is not None
        mock_publish.assert_called_once()
        call_args = mock_publish.call_args
        assert call_args[0][0] == "order.created"
        assert call_args[0][1]["order_id"] == order.order_id
        assert call_args[0][1]["email"] == email
        assert call_args[0][1]["items"] == items

    @patch("app.services.order_service.publish_event")
    def test_create_order_with_multiple_items(self, mock_publish, db_session):
        """Deve criar pedido com múltiplos itens."""
        items = [
            {"product_id": 1, "quantity": 2},
            {"product_id": 2, "quantity": 5},
            {"product_id": 3, "quantity": 1},
        ]

        order = create_order(db_session, items, "test@test.com")

        payload = mock_publish.call_args[0][1]
        assert len(payload["items"]) == 3


class TestProductService:
    """Testes para product_service."""

    def test_create_product_via_service(self, db_session):
        """Deve criar produto via service."""
        from app.schemas.product import ProductCreate

        product_data = ProductCreate(
            name="Notebook", quantity_on_hand=50, average_cost=2500.00
        )

        product = create_product(db_session, product_data)

        assert product is not None
        assert product.name == "Notebook"
        assert product.quantity_on_hand == 50
        assert product.average_cost == 2500.00


class TestStockService:
    """Testes para stock_service."""

    @patch("app.services.stock_service.get_db")
    def test_reserve_stock_success(self, mock_get_db, db_session):
        """Deve reservar estoque com sucesso."""
        # Criar produto com estoque
        product = repo_create_product(
            db_session, name="Produto", quantity_on_hand=100, average_cost=10.0
        )

        # Mock get_db para retornar a sessão de teste
        def mock_db_gen():
            yield db_session

        mock_get_db.return_value = mock_db_gen()

        items = [{"product_id": product.product_id, "quantity": 10}]
        movements = reserve_stock(items)

        assert len(movements) == 1
        assert movements[0].quantity == 10
        assert movements[0].movement_type == "saida"

        # Verificar que o estoque foi reduzido
        db_session.refresh(product)
        assert product.quantity_on_hand == 90

    @patch("app.services.stock_service.get_db")
    def test_reserve_stock_insufficient_stock(self, mock_get_db, db_session):
        """Deve falhar quando estoque é insuficiente."""
        product = repo_create_product(
            db_session, name="Produto", quantity_on_hand=5, average_cost=10.0
        )

        def mock_db_gen():
            yield db_session

        mock_get_db.return_value = mock_db_gen()

        items = [{"product_id": product.product_id, "quantity": 10}]

        with pytest.raises(Exception) as exc_info:
            reserve_stock(items)

        assert "Estoque insuficiente" in str(exc_info.value)

    @patch("app.services.stock_service.get_db")
    def test_reserve_stock_product_not_found(self, mock_get_db, db_session):
        """Deve falhar quando produto não existe."""

        def mock_db_gen():
            yield db_session

        mock_get_db.return_value = mock_db_gen()

        items = [{"product_id": 999, "quantity": 1}]

        with pytest.raises(Exception) as exc_info:
            reserve_stock(items)

        assert "não encontrado" in str(exc_info.value)


class TestPaymentService:
    """Testes para payment_service."""

    def test_process_payment_success(self):
        """Deve processar pagamento com sucesso."""
        payment_data = {"order_id": 1, "amount": 100.0}

        result = process_payment(payment_data)

        assert result is True

    def test_process_payment_with_order_id(self):
        """Deve processar pagamento com order_id."""
        payment_data = {"order_id": 123, "email": "test@test.com"}

        result = process_payment(payment_data)

        assert result is True


class TestEmailService:
    """Testes para email_service."""

    @patch("app.services.email_service.settings")
    def test_send_email_without_smtp_config(self, mock_settings):
        """Deve retornar False se SMTP não estiver configurado."""
        mock_settings.smtp_host = ""

        result = send_email("to@test.com", "Subject", "Body")

        assert result is False

    @patch("app.services.email_service.settings")
    @patch("smtplib.SMTP")
    def test_send_email_success(self, mock_smtp, mock_settings):
        """Deve enviar email com sucesso."""
        mock_settings.smtp_host = "smtp.test.com"
        mock_settings.smtp_port = 587
        mock_settings.smtp_user = "user"
        mock_settings.smtp_password = "pass"
        mock_settings.smtp_from = "from@test.com"
        mock_settings.smtp_tls = True

        mock_server = MagicMock()
        mock_smtp.return_value.__enter__ = MagicMock(return_value=mock_server)
        mock_smtp.return_value.__exit__ = MagicMock(return_value=False)

        result = send_email("to@test.com", "Subject", "Body")

        assert result is True
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with("user", "pass")
        mock_server.sendmail.assert_called_once()

    @patch("app.services.email_service.send_email")
    def test_send_order_processed_email(self, mock_send):
        """Deve enviar email de pedido processado."""
        mock_send.return_value = True

        result = send_order_processed_email(123, "cliente@test.com")

        assert result is True
        mock_send.assert_called_once()
        call_args = mock_send.call_args
        assert "123" in call_args[0][1]  # subject contém order_id
        assert "processado" in call_args[0][1].lower()

    @patch("app.services.email_service.send_email")
    def test_send_payment_failed_email(self, mock_send):
        """Deve enviar email de pagamento falhou."""
        mock_send.return_value = True

        result = send_payment_failed_email(456, "cliente@test.com", "Cartão recusado")

        assert result is True
        mock_send.assert_called_once()
        call_args = mock_send.call_args
        assert "456" in call_args[0][1]  # subject contém order_id
        assert "Cartão recusado" in call_args[0][2]  # body contém reason
