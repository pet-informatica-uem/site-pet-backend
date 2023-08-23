from fastapi.testclient import TestClient
from fastapi import FastAPI

from datetime import datetime, timedelta

from src.modelos.usuario.usuarioClad import UsuarioCriar
from src.autenticacao.jwtoken import gerarTokenAtivaConta
from main import petBack


client = TestClient(petBack)

_idUsuario = None
dadosUsuario = {
    'email': 'ra120113@uem.br',
    'senha': 'Alvaro123456!',
    'cpf': '09934465744',
    'nome': 'Álvaro de Araújo',
    'curso': 'Ciência da Computação'
}

def test_cadastrarUsuario(mocker):
    global _idUsuario
    post_mock = mocker.patch('fastapi.testclient.TestClient.post')
    post_mock.return_value.status_code = 201
    post_mock.return_value.json.return_value = 'id simulado'

    response = client.post("/usuarios", json=dadosUsuario)

    assert response.status_code == 201
    assert type(response.json()) is str
    _idUsuario = response.json()

def test_usuarioJaCadastrado(mocker):
    post_mock = mocker.patch('fastapi.testclient.TestClient.post')
    post_mock.return_value.status_code = 409
    post_mock.return_value.json.return_value = {'message': 'Usuário já existe no banco de dados'}

    response = client.post("/usuarios", json=dadosUsuario)

    assert response.status_code == 409
    assert response.json() == {'message': 'Usuário já existe no banco de dados'}

def test_deletarUsuarioNaoAutenticado(mocker):
    delete_mock = mocker.patch('fastapi.testclient.TestClient.delete')
    delete_mock.return_value.status_code = 401
    delete_mock.return_value.json.return_value = {'detail': 'Not authenticated'}

    response = client.delete(f"/usuarios/{_idUsuario}")

    assert response.status_code == 401
    assert response.json() == {'detail': 'Not authenticated'}

def test_loginSemConfirmacao(mocker):
    post_mock = mocker.patch('fastapi.testclient.TestClient.post')
    post_mock.return_value.status_code = 401
    post_mock.return_value.json.return_value = {"message": "Erro genérico."}

    response = client.post("/usuarios/login", data={'username': 'ra120113@uem.br',
                                                    'password': 'Alvaro123456!'})
    
    assert response.status_code == 401
    assert response.json() == {"message": "Erro genérico."}

def test_confirmarEmail(mocker):
    get_mock = mocker.patch('fastapi.testclient.TestClient.get')

    token :str = gerarTokenAtivaConta(_idUsuario, dadosUsuario['email'], timedelta(days=1))

    response = client.get(f"/usuarios/confirmar-email/{token}")

    assert response.status_code == 200
    assert response.json() is _idUsuario

