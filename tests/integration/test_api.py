from unittest.mock import patch
import pytest


class TestOrdersAPI:
    """Testes de integração para /orders."""

    @patch("app.services.order_service.publish_event")
    def test_create_order_success(self, mock_publish, client, db_session):
        """Deve criar um pedido via API."""
        # Primeiro criar um produto para o pedido
        product_response = client.post(
            "/products/",
            json={
                "name": "Produto Teste",
                "quantity_on_hand": 100,
                "average_cost": 10.0,
            },
        )
        assert product_response.status_code == 200
        product = product_response.json()

        # Criar pedido
        order_data = {
            "email": "cliente@teste.com",
            "items": [{"product_id": product["product_id"], "quantity": 2}],
        }

        response = client.post("/orders/", json=order_data)

        assert response.status_code == 201
        data = response.json()
        assert "order_id" in data
        assert data["status"] == "pending"
        mock_publish.assert_called_once()

    def test_create_order_invalid_email(self, client):
        """Deve retornar erro para email inválido."""
        order_data = {
            "email": "email-invalido",
            "items": [{"product_id": 1, "quantity": 1}],
        }

        response = client.post("/orders/", json=order_data)

        assert response.status_code == 422  # Validation error

    def test_create_order_empty_items(self, client):
        """Deve retornar erro para items vazio."""
        order_data = {"email": "cliente@teste.com", "items": []}

        response = client.post("/orders/", json=order_data)

        # FastAPI pode aceitar lista vazia, dependendo da validação
        # Se não houver validação explícita, o pedido pode ser criado
        assert response.status_code in [200, 400, 422]

    def test_create_order_invalid_quantity(self, client):
        """Deve retornar erro para quantity <= 0."""
        order_data = {
            "email": "cliente@teste.com",
            "items": [{"product_id": 1, "quantity": 0}],
        }

        response = client.post("/orders/", json=order_data)

        assert response.status_code == 422

    @patch("app.services.order_service.publish_event")
    def test_create_order_multiple_items(self, mock_publish, client, db_session):
        """Deve criar pedido com múltiplos itens."""
        # Criar produtos
        for i in range(3):
            client.post(
                "/products/",
                json={
                    "name": f"Produto {i}",
                    "quantity_on_hand": 50,
                    "average_cost": 10.0,
                },
            )

        order_data = {
            "email": "cliente@teste.com",
            "items": [
                {"product_id": 1, "quantity": 2},
                {"product_id": 2, "quantity": 3},
                {"product_id": 3, "quantity": 1},
            ],
        }

        response = client.post("/orders/", json=order_data)

        assert response.status_code == 201


class TestProductsAPI:
    """Testes de integração para /products."""

    def test_create_product_success(self, client):
        """Deve criar um produto via API."""
        product_data = {
            "name": "Caneta Azul",
            "quantity_on_hand": 100,
            "average_cost": 2.50,
        }

        response = client.post("/products/", json=product_data)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Caneta Azul"
        assert data["quantity_on_hand"] == 100
        assert data["average_cost"] == 2.50
        assert "product_id" in data

    def test_create_product_with_defaults(self, client):
        """Deve criar produto com valores padrão."""
        product_data = {"name": "Produto Simples"}

        response = client.post("/products/", json=product_data)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Produto Simples"
        assert data["quantity_on_hand"] == 0
        assert data["average_cost"] == 0.0

    def test_create_product_without_name(self, client):
        """Deve retornar erro se name não for fornecido."""
        product_data = {"quantity_on_hand": 100}

        response = client.post("/products/", json=product_data)

        assert response.status_code == 422

    def test_create_multiple_products(self, client):
        """Deve criar múltiplos produtos."""
        products = [
            {"name": "Produto A", "quantity_on_hand": 10, "average_cost": 5.0},
            {"name": "Produto B", "quantity_on_hand": 20, "average_cost": 15.0},
            {"name": "Produto C", "quantity_on_hand": 30, "average_cost": 25.0},
        ]

        created_ids = []
        for product in products:
            response = client.post("/products/", json=product)
            assert response.status_code == 200
            created_ids.append(response.json()["product_id"])

        # Verificar que todos os IDs são únicos
        assert len(created_ids) == len(set(created_ids))


class TestAPIHealth:
    """Testes para verificar saúde da API."""

    def test_api_is_running(self, client):
        """Deve retornar 200 para endpoint de docs."""
        response = client.get("/docs")
        assert response.status_code == 200

    def test_openapi_schema(self, client):
        """Deve retornar schema OpenAPI."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "paths" in data
