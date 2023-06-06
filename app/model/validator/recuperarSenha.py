from pymongo import MongoClient
from cerberus import Validator


class ValidarRecuperacaoSenha:
    def __init__(self):
        cliente = MongoClient()
        db = cliente["petBD"]
        self.__colecao = db["recuperarSenha"]

    def usuario(self) -> Validator:
        self.__colecao.create_index("idUsuario", unique=True)

        schemaUsuarios = {
            "idUsuario": {"type": "string", "required": True},
            "codigo": {"type": "string", "required": True},
            "data criacao": {"type": "datetime"},
        }

        validadorUsuarios = Validator(schemaUsuarios)
        return validadorUsuarios
