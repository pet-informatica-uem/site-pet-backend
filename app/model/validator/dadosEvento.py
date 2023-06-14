from pymongo import MongoClient
from cerberus import Validator


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
            "vagas ofertadas": {
                "type": "dict",
                "required": True,
                "schema": {
                    "vagas com notebook": {"type": "integer", "required": True},
                    "vagas sem notebook": {"type": "integer", "required": True},
                    "vagas preenchidas com notebook": {"type": "integer", "required": True},
                    "vagas preenchidas sem notebook": {"type": "integer", "required": True},
                },
            },
            "carga horária": {"type": "string", "required": True},
            "valor": {"type": "integer", "required": True},
            "arte evento": {"type": "string", "required": True},
            "arte qrcode": {"type": "string", "required": False},
        }

        validadorEvento = Validator(schemaEvento)
        return validadorEvento
