from cerberus import Validator
from pymongo import MongoClient


class ValidarEvento:
    def __init__(self):
        cliente = MongoClient()
        db = cliente["petBD"]
        self.__colecao = db["eventos"]

    def evento(self) -> Validator:
        self.__colecao.create_index("nome evento", unique=True)

        schemaEvento = {
            "nome evento": {"type": "string", "required": True},
            "resumo": {"type": "string", "required": True},
            "pré-requisitos": {"type": "string", "required": True},
            "data criação": {"type": "datetime", "required": True},
            "data/hora evento": {"type": "datetime", "required": True},
            "data inicio inscrição": {"type": "datetime", "required": True},
            "data fim inscrição": {"type": "datetime", "required": True},
            "local": {"type": "string", "required": True},
            "carga horária": {"type": "integer", "required": True},
            "valor": {"type": "float", "required": True},
            "arte evento": {"type": "string", "required": True},
            "arte qrcode": {"type": "string", "required": False},
        }

        validadorEvento = Validator(schemaEvento) # type: ignore
        return validadorEvento
