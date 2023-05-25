from datetime import datetime

from usuario import criarUsuario

dadosUsuario = {
    'nome': 'Alice',
    'email': 'alice@example.com',
    'cpf': '1234954345',
    'curso': 'Ciência da Computação',
    'status': 'ativo',
    'senha': 'password123',
    'data_criacao': datetime.now()
}
criarUsuario(dadosUsuario)
