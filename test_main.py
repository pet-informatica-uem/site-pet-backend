import os

# Configurações de ambiente para testes
os.environ["PET_API_MOCK_EMAIL"] = "true"
os.environ["PET_API_MOCK_BD"] = "true"

from fastapi.testclient import TestClient

from main import petBack


testClient = TestClient(petBack)


def test_criar_usuario():
    response = testClient.post(
        "/usuarios",
        json={
            "nome": "Usuario Teste",
            "email": "user@example.com",
            "cpf": "05685287003",
            "senha": "Senha123!",
            "curso": "Ciência da Computação",
        },
    )

    assert response.status_code == 201
