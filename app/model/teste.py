from datetime import datetime

from usuarioBD import UsuarioBD

"""dadosUsuario = {
    'nome': 'nome',
    'email': 'email@example.com',
    'cpf': '00000000000',
    'curso': 'curso',
    'estado da conta': 'ativo',     ativo ou inativo 
    'senha': 'senha123',   
    'tipo conta': 'petiano',      petiano, petiano egresso ou estudante
    'tempo de pet': {},
    'redes sociais': {},        github, linkedin, instagram, twitter
    'foto perfil': 'images/fotoUsuario/alguem.jpg',     passar a url da imagem
    'data criacao': datetime.now()
}"""

dadosUsuario = {
    "nome": "evento",
    "email": "even7to@example.com",
    "cpf": "00890500070",
    "curso": "curso",
    "estado da conta": "ativo",
    "senha": "senha123",
    "tipo conta": "petiano",
    "tempo de pet": {},
    "redes sociais": {},
    "foto perfil": "images/fotoUsuario/alguem.jpg",
    "data criacao": datetime.now(),
}

usuarioBD = UsuarioBD()
# erros = usuarioBD.criarUsuario(dadosUsuario)
# print(erros)

# print(usuarioBD.deletarUsuario('647cb6c4f17dbcd7f7d7d80a'))
# print(usuarioBD.atualizarUsuario('647cb6c4f17dbcd7f7d7d80a', dadosUsuario))
print(usuarioBD.getUsuario("647cc45b9f546e9fde0dfac0"))
# print(usuarioBD.getListaUsuarios())
