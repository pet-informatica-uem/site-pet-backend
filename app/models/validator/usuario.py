from pymongo import MongoClient
from cerberus import Validator

class ValidarUsuario():
    def __init__(self):
        cliente = MongoClient()
        db = cliente['petBD']
        self.__colecao = db['usuarios']

    def Usuario(self):
        self.__colecao.create_index('cpf', unique=True)
        self.__colecao.create_index('email', unique=True)

        schemaUsuarios = {
            'nome': {'type': 'string', 'required': True},
            'email': {'type': 'string', 'required': True},
            'cpf': {'type': 'string', 'required': True},
            'curso': {'type': 'string', 'required': True},
            'estado': {'type': 'string', 'required': True, 'allowed': ['ativo', 'inativo']},
            'senha': {'type': 'string', 'required': True, 'minlength': 8},
            'petiano': {'type': 'string', 'required': True, 'allowed': ['sim', 'nao', 'egresso']},
            'data_criacao': {'type': 'datetime'}
        }

        validadorUsuarios = Validator(schemaUsuarios)
        return validadorUsuarios