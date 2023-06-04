from datetime import datetime
from usuarioBD import UsuarioBD

'''dadosUsuario = {
    'nome': 'nome',
    'email': 'email@example.com',
    'cpf': '00000000000',
    'curso': 'curso',
    'estado da conta': 'ativo',     ativo ou inativo 
    'senha': 'senha123',   
    'tipo conta': 'petiano',      petiano, petiano egresso ou estudante
    'tempo de pet': {},
    'redes sociais': {},        github, linkedin, instagram, twitter
    'data_criacao': datetime.now()
}'''


usuarioBD = UsuarioBD()
# erros = usuarioBD.criarUsuario(dadosUsuario)
# print(erros)

# print('\n\n\n')
# print(usuarioBD.getIdUsuario(dadosUsuario['email']))
# print(usuarioBD.getPetiano(usuarioBD.getIdUsuario(dadosUsuario['email'])))
# print(usuarioBD.getUsuario(usuarioBD.getIdUsuario(dadosUsuario['email'])))

