from pymongo import MongoClient
from cerberus import Validator

cliente = MongoClient()
db = cliente['petBD']
colecao = db['usuarios']

colecao.create_index('cpf', unique=True)

schemaUsuarios = {
    'nome': {'type': 'string', 'required': True},
    'email': {'type': 'string', 'required': True},
    'cpf': {'type': 'string', 'required': True},
    'curso': {'type': 'string', 'required': True},
    'status': {'type': 'string', 'required': True, 'allowed': ['ativo', 'inativo', 'bloqueado']},
    'senha': {'type': 'string', 'required': True, 'minlength': 8},
    'data_criacao': {'type': 'datetime'}
}

validadorUsuarios = Validator(schemaUsuarios)

def criarUsuario(dadoUsuario):
    if validadorUsuarios.validate(dadoUsuario):
        colecao.insert_one(dadoUsuario)
        print('Usuário criado:', dadoUsuario)
    else:
        print('Erro criação usuário:', validadorUsuarios.errors)


