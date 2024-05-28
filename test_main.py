import os
import random

from cpf_generator import CPF

# Configurações de ambiente para testes
os.environ["PET_API_MOCK_EMAIL"] = "true"
os.environ["PET_API_MOCK_BD"] = "true"

import pytest
from fastapi.testclient import TestClient

from main import petBack
from src.modelos.bd import UsuarioBD

testClient = TestClient(petBack)


def test_usuario_cadastrar():
    data = cria_usuario()

    usuario = UsuarioBD().buscar("email", data["email"])

    assert usuario.id == data["id"]
    assert usuario.nome == "Usuario Teste"
    assert usuario.email == data["email"]
    assert usuario.cpf == data["cpf"]
    assert usuario.curso == "Ciência da Computação"


def test_usuario_atualizar():
    data = cria_usuario()

    confirma_usuario(data["email"])

    auth_header = loga_usuario(data["email"])

    response = testClient.patch(
        f"/usuarios/{data[id]}", json={"nome": "Novo Nome"}, headers=auth_header
    )
    assert response.status_code == 200

    response = testClient.get("/usuarios/eu", headers=auth_header)

    assert response.status_code == 200

    assert response.json()["nome"] == "Novo Nome"
    assert response.json()["cpf"] == data["cpf"]


def test_usuario_listar(auth_usuario_petiano):
    cria_usuario()
    cria_usuario()

    response = testClient.get("/usuarios")

    assert response.status_code == 401

    response = testClient.get("/usuarios", headers=auth_usuario_petiano)

    assert response.status_code == 200
    assert len(response.json()) == 3

    unique_ids = set(
        [response.json()[0]["id"], response.json()[1]["id"], response.json()[2]["id"]]
    )

    assert len(unique_ids) == 3


@pytest.fixture
def auth_usuario_petiano():
    data = cria_usuario()

    usuario = UsuarioBD().buscar("email", data["email"])
    usuario.email = "petiano@email.com"
    usuario.tipoConta = "petiano"
    usuario.emailConfirmado = True

    UsuarioBD().atualizar(usuario)

    yield loga_usuario("petiano@email.com")


def cria_usuario() -> dict:
    """
    Cria um usuário aleatório e retorna um dicionário com os dados

    Return:
        dict: Dicionário com os dados do usuário (email, cpf e id)
    """
    # Gera um email e cpf aleatórios
    email = f"user{random.randint(0, 1000)}@example.com"
    cpf = CPF.generate()

    payload = {
        "nome": "Usuario Teste",
        "email": email,
        "cpf": cpf,
        "senha": "Senha123!",
        "curso": "Ciência da Computação",
    }

    response = testClient.post("/usuarios", json=payload)

    assert response.status_code == 201

    ret_dict = {"email": email, "cpf": cpf, "id": response.json()}

    return ret_dict


def confirma_usuario(email) -> None:
    """
    Confirma o email de um usuário no banco de dados.
    """
    usuario = UsuarioBD().buscar("email", email)
    usuario.emailConfirmado = True

    UsuarioBD().atualizar(usuario)


def loga_usuario(email) -> dict:
    """
    Loga um usuário e retorna o bearer token de autenticação
    """

    payload = {
        "grant_type": "password",
        "username": email,
        "password": "Senha123!",
        "scope": "",
        "client_id": "string",
        "client_secret": "string",
    }

    response = testClient.post(
        "/usuarios/login",
        data=payload,
    )

    assert response.status_code == 200

    return {"Authorization": f"Bearer {response.json()['access_token']}"}
