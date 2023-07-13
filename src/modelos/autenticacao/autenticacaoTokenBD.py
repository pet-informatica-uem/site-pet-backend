from datetime import datetime

from bson.objectid import ObjectId
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

from src.modelos.autenticacao.authToken import ValidarAuthToken


class AuthTokenBD:
    def __init__(self):
        cliente = MongoClient()
        db = cliente["petBD"]
        self.__colecao = db["auth tokens"]
        self.__validarDados = ValidarAuthToken().authToken()

    def criarToken(self, dadoToken: dict) -> dict:
        if self.__validarDados.validate(dadoToken):  # type: ignore
            try:
                dadoToken.update({"idUsuario": ObjectId(dadoToken["idUsuario"])})
                resultado = self.__colecao.insert_one(dadoToken)
                return {
                    "mensagem": resultado.inserted_id,
                    "status": "200",
                }
            except DuplicateKeyError:
                return {"mensagem": "Token já existe", "status": "409"}
        else:
            return {"mensagem": self.__validarDados.errors, "status": "400"}  # type: ignore

    def deletarToken(self, token: str) -> dict:
        resultado = self.__colecao.delete_one({"_id": token})
        if resultado.deleted_count == 1:
            return {"mensagem": "Token removido com sucesso", "status": "200"}
        else:
            return {"mensagem": "Token não encontrado", "status": "404"}

    def getIdUsuarioDoToken(self, token: str) -> dict:
        if resultado := self.__colecao.find_one({"_id": token}):
            if resultado["validade"] < datetime.now():
                return {"mensagem": "Token não encontrado", "status": "404"}

            return {
                "mensagem": resultado["idUsuario"],
                "status": "200",
            }
        else:
            return {"mensagem": "Token não encontrado", "status": "404"}

    def deletarTokensUsuario(self, idUsuario: str) -> dict:
        resultado = self.__colecao.delete_many({"idUsuario": idUsuario})
        if resultado.deleted_count > 0:
            return {"status": "200", "mensagem": "Os tokens do usuário foram deletados"}
        else:
            return {"status": "404", "mensagem": "Usuário não encontrado"}
