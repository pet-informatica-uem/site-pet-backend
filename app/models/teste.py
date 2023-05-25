from datetime import datetime

from usuario import create_user

user_data = {
    'nome': 'Alice',
    'email': 'alice@example.com',
    'cpf': '12345678900',
    'curso': 'Ciência da Computação',
    'status': 'ativo',
    'senha': 'password123',
    'data_criacao': datetime.now()
}
create_user(user_data)
