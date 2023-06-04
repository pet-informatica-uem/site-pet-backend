from pymongo import MongoClient
from cerberus import Validator


class ValidarUsuario:
    def __init__(self):
        cliente = MongoClient()
        db = cliente["petBD"]
        self.__colecao = db["usuarios"]

    def usuario(self) -> Validator:
        self.__colecao.create_index("cpf", unique=True)
        self.__colecao.create_index("email", unique=True)

        schemaUsuarios = {
            "nome": {"type": "string", "required": True},
            "email": {"type": "string", "required": True},
            "cpf": {"type": "string", "required": True},
            "curso": {"type": "string", "required": True},
            "estado da conta": {
                "type": "string",
                "required": True,
                "allowed": ["ativo", "inativo"],
            },
            "senha": {"type": "string", "required": True},
            "tipo conta": {         # TODO colocar periodo do petiano no PET
                "type": "string",
                "required": True,
                "allowed": ["petiano", "petiano egresso", "estudante"],
            },
            "redes sociais": {
                "type": "dict",         # TODO testar se isso funciona, aqui está dicionário e não lista
                "required": False,
                "schema": {
                    "github": {"type": "string"},
                    "linkedin": {"type": "string"},
                    "instagram": {"type": "string"},
                    "twitter": {"type": "string"},
                },
            },
            "data criacao": {"type": "datetime"},
        }

        validadorUsuarios = Validator(schemaUsuarios)
        return validadorUsuarios
