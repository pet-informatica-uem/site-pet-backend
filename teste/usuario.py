from fastapi.testclient import TestClient

from datetime import timedelta

from src.modelos.usuario.usuarioClad import UsuarioCriar
from src.autenticacao.jwtoken import gerarTokenAtivaConta
from main import petBack

MONGODB_TEST_URL = "mongodb+srv://<username>:<password>@<url>/<db>?retryWrites=true&w=majority"

client = TestClient(petBack)

_idUsuario: str = ""
dadosUsuario = {
    "email": "ra120113@uem.br",
    "senha": "Alvaro123456!",
    "cpf": "09934465744",
    "nome": "Álvaro de Araújo",
    "curso": "Ciência da Computação",
}


def test_cadastrarUsuario():
    global _idUsuario
    response = client.post("/usuarios?banco=TESTE_BD", json=dadosUsuario)

    assert response.status_code == 201
    assert isinstance(response.json(), str)
    _idUsuario = response.json()


def test_usuarioJaCadastrado():
    response = client.post("/usuarios", json=dadosUsuario)

    assert response.status_code == 409
    assert response.json() == {"message": "Usuário já existe no banco de dados"}


# não pode deletar usuário pois o usuário não está autenticado
def test_deletarUsuarioNaoAutenticado():
    response = client.delete(f"/usuarios/{_idUsuario}")

    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


# o email não foi confirmado, por isso não consegue logar
def test_loginSemConfirmacao():
    response = client.post(
        "/usuarios/login",
        data={"username": "ra120113@uem.br", "password": "Alvaro123456!"},
    )

    assert response.status_code == 401
    assert response.json() == {"message": "Erro genérico."}


# como passar esse token?
# o caminho que chega no email é estranho, não é igual o que passo aqui
def test_tokenErroGenerico():
    token: str = gerarTokenAtivaConta(
        _idUsuario, dadosUsuario["email"], timedelta(days=1)
    )
    print('\n\n\n', token)

    response = client.post(f"/usuarios/confirmar-email/?token={token}")

    print(response)
    print(response.json())

    assert response.status_code == 404
    assert response.json() == {"message": "O Usuário não foi encontrado."}


# def test_confirmarEmail():
#     token: str = gerarTokenAtivaConta(
#         _idUsuario, dadosUsuario["email"], timedelta(days=1)
#     )

#     response = client.get(f"/usuarios/confirmar-email/{token[0]}")

#     assert response.status_code == 200
#     assert response.json() is _idUsuario


# daqui para baixo está estranho, está tudo estranho. Revisar

# def test_usuarioLoginErroGEnerico(mocker):
#     post_mock = mocker.patch('fastapi.testclient.TestClient.post')
#     post_mock.return_value.status_code = 401
#     post_mock.return_value.json.return_value = {"message": "Erro genérico."}

#     response = client.post("/usuarios/login", data={'username': dadosUsuario['email'], 'password': dadosUsuario['senha']})

#     assert response.status_code == 401
#     assert response.json() == {"message": "Erro genérico."}


# def test_usuarioNaoEncontrado(mocker):
#     post_mock = mocker.patch("fastapi.testclient.TestClient.post")
#     post_mock.return_value.status_code = 404
#     post_mock.return_value.json.return_value = {
#         "message": "O Usuário não foi encontrado."
#     }

#     response = client.post(
#         "/usuarios/login",
#         data={
#             "username": dadosUsuario["email"],
#             "password": '0',
#         },
#     )

#     print(response.json())
#     print(response.status_code)
#     print(response)

#     assert response.status_code == 404
#     assert response.json() == {"message": "O Usuário não foi encontrado."}


# def test_usuarioLogin():
#     response = client.post('/usuarios/login', data={'username': dadosUsuario['email'][0], 'password': dadosUsuario['senha']})

#     assert response.status_code == 200
#     assert type(response.json()) is dict