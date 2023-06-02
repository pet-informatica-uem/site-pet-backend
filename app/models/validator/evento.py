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
            "data evento": {"type": "datetime", "required": True},
            "hora evento": {"type": "string", "required": True},
            "data inicio inscrição": {"type": "datetime", "required": True},
            "data fim inscrição": {"type": "datetime", "required": True},
            "local": {"type": "string", "required": True},
            "total vagas ofertadas": {"type": "string", "required": True},
            "laboratorio": {
                "type": "string",
                "required": True,
                "allowed": ["sim", "nao"],
            },
            "vagas com notebook": {"type": "string", "required": True},
            "vagas sem notebook": {"type": "string", "required": True},
            "carga horária": {"type": "string", "required": True},
            "pago": {"type": "string", "required": True, "allowed": ["sim", "nao"]},
            "valor": {"type": "string", "required": False},
            "arte evento": {"type": "binary", "required": True},
            "qr code": {"type": "string", "required": True, "allowed": ["sim", "nao"]},
            "arte qrcode": {"type": "binary", "required": False},
            "inscritos": {
                "type": "list",
                "required": False,
                "schema": {
                    "type": "dict",
                    "schema": {
                        "idUsuario": {"type": "objectid"},
                        "data": {"type": "datetime"},
                        "hora": {"type": "string"},
                    },
                },
            },
            "presentes": {
                "type": "list",
                "required": False,
                "schema": {
                    "type": "dict",
                    "schema": {
                        "idUsuario": {"type": "objectid"},
                        "data": {"type": "datetime"},
                        "hora": {"type": "string"},
                    },
                },
            },
        }

        validadorEvento = Validator(schemaEvento)
        return validadorEvento
