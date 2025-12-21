import json
from unittest.mock import MagicMock, patch
import pytest

from app.core.rabbitmq import publish_event, get_connection
from app.workers.order_worker import callback as order_callback
from app.workers.payment_worker import callback as payment_callback
from app.workers.notify_worker import callback as notify_callback
from app.workers.stock_worker import callback as stock_callback
from app.workers.order_worker import QUEUE_NAME


class TestOrderWorker:
    """Testes para order_worker."""

    @patch("app.workers.order_worker.publish_event")
    def test_callback_processes_message(self, mock_publish):
        """Deve processar mensagem e publicar payment.processing."""

        # Mock do channel
        ch = MagicMock()
        method = MagicMock()
        method.delivery_tag = "tag123"

        # Dados da mensagem
        data = {
            "order_id": 1,
            "email": "test@test.com",
            "items": [{"product_id": 1, "quantity": 2}],
        }
        body = json.dumps(data).encode()

        order_callback(ch, method, None, body)

        # Verifica que publicou evento payment.processing
        mock_publish.assert_called_once_with("payment.processing", data)
        ch.basic_ack.assert_called_once_with(delivery_tag="tag123")

    @patch("app.workers.order_worker.get_connection")
    def test_worker_connects_to_rabbitmq(self, mock_get_conn):
        """Deve conectar ao RabbitMQ e declarar exchange/queue."""
        mock_conn = MagicMock()
        mock_channel = MagicMock()
        mock_conn.channel.return_value = mock_channel
        mock_get_conn.return_value = mock_conn

        assert QUEUE_NAME == "order_queue"


class TestStockWorker:
    """Testes para stock_worker."""

    @patch("app.workers.stock_worker.reserve_stock")
    @patch("app.workers.stock_worker.publish_event")
    def test_callback_success(self, mock_publish, mock_reserve):
        """Deve reservar estoque e publicar order.processed."""

        mock_reserve.return_value = [MagicMock()]

        ch = MagicMock()
        method = MagicMock()
        method.delivery_tag = "tag456"

        data = {
            "order_id": 1,
            "email": "test@test.com",
            "items": [{"product_id": 1, "quantity": 2}],
        }
        body = json.dumps(data).encode()

        stock_callback(ch, method, None, body)

        mock_reserve.assert_called_once_with(data["items"])
        mock_publish.assert_called_once()
        call_args = mock_publish.call_args
        assert call_args[0][0] == "order.processed"
        ch.basic_ack.assert_called_once()

    @patch("app.workers.stock_worker.reserve_stock")
    @patch("app.workers.stock_worker.publish_event")
    def test_callback_handles_error(self, mock_publish, mock_reserve):
        """Deve tratar erro de reserva sem crashar."""

        mock_reserve.side_effect = Exception("Estoque insuficiente")

        ch = MagicMock()
        method = MagicMock()
        method.delivery_tag = "tag789"

        data = {"order_id": 1, "items": [{"product_id": 999, "quantity": 100}]}
        body = json.dumps(data).encode()

        # Não deve levantar exceção
        stock_callback(ch, method, None, body)

        mock_publish.assert_not_called()
        ch.basic_ack.assert_called_once()


class TestPaymentWorker:
    """Testes para payment_worker."""

    @patch("app.workers.payment_worker.process_payment")
    @patch("app.workers.payment_worker.publish_event")
    def test_callback_success(self, mock_publish, mock_process):
        """Deve processar pagamento e publicar payment.completed."""

        mock_process.return_value = True

        ch = MagicMock()
        method = MagicMock()
        method.delivery_tag = "tagabc"

        data = {"order_id": 1, "email": "test@test.com"}
        body = json.dumps(data).encode()

        payment_callback(ch, method, None, body)

        mock_process.assert_called_once_with(data)
        mock_publish.assert_called_once_with("payment.completed", data)
        ch.basic_ack.assert_called_once()

    @patch("app.workers.payment_worker.process_payment")
    @patch("app.workers.payment_worker.publish_event")
    def test_callback_failure(self, mock_publish, mock_process):
        """Deve publicar payment.failed em caso de erro."""

        mock_process.side_effect = Exception("Pagamento recusado")

        ch = MagicMock()
        method = MagicMock()
        method.delivery_tag = "tagdef"

        data = {"order_id": 1, "email": "test@test.com"}
        body = json.dumps(data).encode()

        payment_callback(ch, method, None, body)

        mock_publish.assert_called_once_with("payment.failed", data)
        ch.basic_ack.assert_called_once()


class TestNotifyWorker:
    """Testes para notify_worker."""

    @patch("app.workers.notify_worker.send_order_processed_email")
    @patch("app.workers.notify_worker.settings")
    def test_callback_order_processed(self, mock_settings, mock_send_email):
        """Deve enviar email de pedido processado."""

        mock_settings.notify_email = ""
        mock_send_email.return_value = True

        ch = MagicMock()
        method = MagicMock()
        method.routing_key = "order.processed"
        method.delivery_tag = "tag111"

        data = {"order_id": 1, "email": "cliente@test.com"}
        body = json.dumps(data).encode()

        notify_callback(ch, method, None, body)

        mock_send_email.assert_called_once_with(1, "cliente@test.com")
        ch.basic_ack.assert_called_once()

    @patch("app.workers.notify_worker.send_payment_failed_email")
    @patch("app.workers.notify_worker.settings")
    def test_callback_payment_failed(self, mock_settings, mock_send_email):
        """Deve enviar email de pagamento falhou."""

        mock_settings.notify_email = ""
        mock_send_email.return_value = True

        ch = MagicMock()
        method = MagicMock()
        method.routing_key = "payment.failed"
        method.delivery_tag = "tag222"

        data = {"order_id": 2, "email": "cliente@test.com", "reason": "Cartão recusado"}
        body = json.dumps(data).encode()

        notify_callback(ch, method, None, body)

        mock_send_email.assert_called_once_with(
            2, "cliente@test.com", "Cartão recusado"
        )
        ch.basic_ack.assert_called_once()

    @patch("app.workers.notify_worker.send_order_processed_email")
    @patch("app.workers.notify_worker.settings")
    def test_callback_uses_default_email(self, mock_settings, mock_send_email):
        """Deve usar email padrão se não houver email no payload."""

        mock_settings.notify_email = "default@test.com"
        mock_send_email.return_value = True

        ch = MagicMock()
        method = MagicMock()
        method.routing_key = "order.processed"
        method.delivery_tag = "tag333"

        data = {"order_id": 3}  # Sem email
        body = json.dumps(data).encode()

        notify_callback(ch, method, None, body)

        mock_send_email.assert_called_once_with(3, "default@test.com")


class TestRabbitMQConnection:
    """Testes para conexão RabbitMQ."""

    @patch("app.core.rabbitmq.pika.BlockingConnection")
    @patch("app.core.rabbitmq.settings")
    def test_get_connection(self, mock_settings, mock_conn):
        """Deve criar conexão com parâmetros corretos."""

        mock_settings.rabbitmq_host = "localhost"
        mock_settings.rabbitmq_port = 5672
        mock_settings.rabbitmq_user = "guest"
        mock_settings.rabbitmq_password = "guest"

        get_connection()

        mock_conn.assert_called_once()

    @patch("app.core.rabbitmq.get_connection")
    def test_publish_event(self, mock_get_conn):
        """Deve publicar evento no exchange."""

        mock_conn = MagicMock()
        mock_channel = MagicMock()
        mock_conn.channel.return_value = mock_channel
        mock_get_conn.return_value = mock_conn

        payload = {"test": "data"}
        publish_event("test.event", payload)

        mock_channel.exchange_declare.assert_called_once()
        mock_channel.basic_publish.assert_called_once()
        mock_conn.close.assert_called_once()
