from cerberus import Validator
from pymongo import MongoClient


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

        validadorAuthToken = Validator(schemaAuthToken)  # type: ignore
        return validadorAuthToken
