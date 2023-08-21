from fastapi.testclient import TestClient
from fastapi import FastAPI

from src.modelos.usuario.usuario import TipoConta, Usuario, Petiano
from src.modelos.usuario.usuarioClad import UsuarioCriar


app = FastAPI()
client = TestClient(app)

def test_cadastroUsuario():
    usuario = UsuarioCriar(
        email='ra120113@uem.br',
        senha='Alvaro123456!',
        cpf='09934465744',
        nome='Álvaro de Araújo',
        curso='Ciência da Computação',)

    response = client.post("/usuarios", json={'nome': 'Álvaro de Araújo', 
                                             'cpf': '09934465744', 
                                             'email': 'ra120113@uem.br',
                                             'curso': 'Ciência da Computação',
                                             'senha': 'Alvaro123456!'})
    assert response.status_code == 201
    assert "access_token" in response.json()


    # id :str = cadastrarUsuario(nomeCompleto, cpf, email, senha, curso)
    # assert id is not None

# verificar como esse testclient funciona, talvez tenha mais funções que usem ele
# def test_autenticar():
#     client = testclient.TestClient(app)
#     response = client.post("/token", data={"username": "ra120113@uem.br", "password": "Alvaro123456!!"})
#     assert response.status_code == 200
# #     assert "access_token" in response.json()

# def test_listarUsuarios():
#     response = client.get("/")
#     usuarios :list = listarUsuarios()
#     assert usuarios is list