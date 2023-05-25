from pymongo import MongoClient
from cerberus import Validator

client = MongoClient()
db = client['petBD']
collection = db['usuarios']

schema = {
    'nome': {'type': 'string', 'required': True},
    'email': {'type': 'string', 'required': True},
    'cpf': {'type': 'string', 'required': True, 'unique': True, 'minlength': 11, 'maxlength': 11, 'regex': '^[0-9]*$'},
    'curso': {'type': 'string', 'required': True},
    'status': {'type': 'string', 'required': True, 'allowed': ['ativo', 'inativo', 'bloqueado']},
    'senha': {'type': 'string', 'required': True, 'minlength': 8},
    'data_criacao': {'type': 'datetime'}
}

v = Validator(schema)

def create_user(user_data):
    if v.validate(user_data):
        collection.insert_one(user_data)
        print('User created:', user_data)
    else:
        print('Error creating user:', v.errors)
