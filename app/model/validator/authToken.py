from pymongo import MongoClient
from cerberus import Validator


class ValidarAuthToken:
    def __init__(self):
        cliente = MongoClient()
        db = cliente["petBD"]
        self.__colecao = db["auth tokens"]

    def authToken(self) -> Validator:
        schemaAuthToken = {
            "_id": {"type": "string", "required": True},
            "idUsuario": {"type": "string", "required": True},
            "validade": {"type": "datetime", "required": True},
        }

        validadorAuthToken = Validator(schemaAuthToken)
        return validadorAuthToken
