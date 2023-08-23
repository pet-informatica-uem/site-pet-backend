from fastapi.testclient import TestClient
from fastapi import FastAPI

from src.modelos.usuario.usuarioClad import UsuarioCriar
from src.autenticacao.jwtoken import recuperarToken
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

def test_cadastrarUsuario():
    global _idUsuario

    response = client.post("/usuarios", json=dadosUsuario)

    assert response.status_code == 201
    assert type(response.json()) is str
    _idUsuario = response.json()


def test_usuarioJaCadastrado():

    response = client.post("/usuarios", json=dadosUsuario)

    assert response.status_code == 409
    assert response.json() == {'message': 'Usuário já existe no banco de dados'}

def test_deletarUsuarioNaoAutenticado():

    response = client.delete(f"/usuarios/{_idUsuario}")

    assert response.status_code == 401
    assert response.json() == {'detail': 'Not authenticated'}

def test_loginSemConfirmacao():
    response = client.post("/usuarios/login", data={'username': 'ra120113@uem.br',
                                                    'password': 'Alvaro123456!'})
    
    assert response.status_code == 401
    assert response.json() == {"message": "Erro genérico."}


# https://github.com/mongomock/mongomock
# https://pypi.org/project/pytest-mock/
# não conecta de verdade com o banco, talvez melhore os testes
def test_confirmarEmail():
    token = recuperarToken(idUsuario=_idUsuario, emailUsuario=dadosUsuario['email'], expiracao=1)

    response = client.get(f"/usuarios/confirmar-email/{token}")
    print(response)
    print(response.json())
    print(response.status_code)