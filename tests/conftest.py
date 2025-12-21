"""
Configuração compartilhada para todos os testes.
"""

import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.db.base import Base
from app.db.session import get_db
from app.main import app


# SQLite em memória para testes
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Cria uma sessão de banco de dados para testes."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Cliente de teste FastAPI com banco de dados mockado."""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def mock_publish_event():
    """Mock para publish_event do RabbitMQ."""
    with patch("app.core.rabbitmq.publish_event") as mock:
        yield mock


@pytest.fixture
def mock_get_connection():
    """Mock para get_connection do RabbitMQ."""
    with patch("app.core.rabbitmq.get_connection") as mock:
        mock_conn = MagicMock()
        mock_channel = MagicMock()
        mock_conn.channel.return_value = mock_channel
        mock.return_value = mock_conn
        yield mock


@pytest.fixture
def mock_smtp():
    """Mock para servidor SMTP."""
    with patch("smtplib.SMTP") as mock:
        mock_server = MagicMock()
        mock.return_value.__enter__ = MagicMock(return_value=mock_server)
        mock.return_value.__exit__ = MagicMock(return_value=False)
        yield mock_server


@pytest.fixture
def sample_order_items():
    """Dados de exemplo para itens de pedido."""
    return [
        {"product_id": 1, "quantity": 2},
        {"product_id": 2, "quantity": 1},
    ]


@pytest.fixture
def sample_product_data():
    """Dados de exemplo para produto."""
    return {
        "name": "Produto Teste",
        "quantity_on_hand": 100,
        "average_cost": 10.50,
    }


@pytest.fixture
def sample_order_create_data():
    """Dados de exemplo para criação de pedido."""
    return {
        "email": "cliente@teste.com",
        "items": [
            {"product_id": 1, "quantity": 2},
        ],
    }
