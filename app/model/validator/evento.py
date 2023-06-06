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
            "nível conhecimento": {
                "type": "string",
                "required": True,
                "allowed": [
                    "Não conheço nada",
                    "Tenho uma noção da lógica",
                    "Programo o básico",
                    "Programo normalmente",
                    "Tenho conhecimento avançado",
                ],
            },
            "data criação": {"type": "datetime", "required": True},
            "data/hora evento": {"type": "datetime", "required": True},
            "data inicio inscrição": {"type": "datetime", "required": True},
            "data fim inscrição": {"type": "datetime", "required": True},
            "local": {"type": "string", "required": True},
            "vagas ofertadas": {
                "type": "dict",
                "required": True,
                "schema": {
                    "total vagas": {"type": "integer", "required": True},
                    "vagas com notebook": {"type": "integer", "required": True},
                    "vagas sem notebook": {"type": "integer", "required": True},
                    "vagas preenchidas": {"type": "integer", "required": True},
                },
            },
            "carga horária": {"type": "string", "required": True},
            "valor": {"type": "integer", "required": True},
            "arte evento": {"type": "string", "required": True},
            "arte qrcode": {"type": "string", "required": False},
            "inscritos": {
                "type": "list",
                "required": False,
                "schema": {
                    "type": "dict",
                    "schema": {
                        "idUsuario": {"type": "string"},
                        "data/hora": {"type": "datetime"},
                        "pagamento": {"type": "boolean"}, 
                    },
                },
            },
            "presentes": {
                "type": "list",
                "required": False,
                "schema": {
                    "type": "dict",
                    "schema": {
                        "idUsuario": {"type": "string"},
                        "data/hora": {"type": "datetime"},
                    },
                },
            },
        }

        validadorEvento = Validator(schemaEvento)
        return validadorEvento
