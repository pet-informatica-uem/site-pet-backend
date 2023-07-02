from pymongo import MongoClient
from cerberus import Validator


class ValidarInscritosEvento:
    def __init__(self):
        cliente = MongoClient()
        db = cliente["petBD"]
        self.__colecao = db["inscritos eventos"]

    def inscritos(self) -> Validator:
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
                                "Não conheço nada",
                                "Tenho uma noção da lógica",
                                "Programo o básico",
                                "Programo normalmente",
                                "Tenho conhecimento avançado",
                            ],
                        },
                        "tipo inscrição": {
                            "type": "string",
                            "required": False,
                            "allowed": ["vaga com notebook", "vaga sem notebook"],
                        },
                    },
                },
            },
        }

        validadorEvento = Validator(schemaEvento)
        return validadorEvento
