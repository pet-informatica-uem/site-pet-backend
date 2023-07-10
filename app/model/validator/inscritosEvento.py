from cerberus import Validator
from pymongo import MongoClient


class ValidarInscritosEvento:
    def __init__(self):
        cliente = MongoClient()
        db = cliente["petBD"]
        self.__colecao = db["inscritos eventos"]

    def vagasEvento(self) -> Validator:
        self.__colecao.create_index("idEvento", unique=True)

        schemaEvento = {
            "idEvento": {"type": "string", "required": True},
            "vagas ofertadas": {
                "type": "dict",
                "required": True,
                "schema": {
                    "vagas com notebook": {"type": "integer", "required": True},
                    "vagas sem notebook": {"type": "integer", "required": True},
                    "vagas preenchidas com notebook": {
                        "type": "integer",
                        "required": True,
                    },
                    "vagas preenchidas sem notebook": {
                        "type": "integer",
                        "required": True,
                    },
                },
            },
        }

        validadorEvento = Validator(schemaEvento)
        return validadorEvento

    def inscricao(self) -> Validator:
        schemaInscricao = {
            "inscritos": {
                "type": "list",
                "required": False,
                "schema": {
                    "type": "dict",
                    "schema": {
                        "idUsuario": {"type": "string"},
                        "data/hora": {"type": "datetime"},
                        "pagamento": {"type": "boolean"},
                        "presente": {"type": "boolean"},
                        "nível conhecimento": {
                            "type": "string",
                            "required": False,
                            "allowed": [
                                "1",
                                "2",
                                "3",
                                "4",
                                "5",
                            ],
                        },
                        "tipo inscrição": {
                            "type": "string",
                            "required": False,
                            "allowed": ["com notebook", "sem notebook"],
                        },
                    },
                },
            },
        }

        validadorInscricao = Validator(schemaInscricao)
        return validadorInscricao
