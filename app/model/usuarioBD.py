from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from bson.objectid import ObjectId
from app.model.validator.usuario import ValidarUsuario


class UsuarioBD:
    def __init__(self):
        cliente = MongoClient()
        db = cliente["petBD"]
        self.__colecao = db["usuarios"]
        self.__validarDados = ValidarUsuario().usuario()

    def criarUsuario(self, dadoUsuario: object) -> dict:
        if self.__validarDados.validate(dadoUsuario):
            try:
                resultado = self.__colecao.insert_one(dadoUsuario)
                return {
                    "mensagem": resultado.inserted_id,
                    "status": "200",
                }
            except DuplicateKeyError:
                return {"mensagem": "CPF ou email já existem", "status": "409"}
        else:
            return {"mensagem": self.__validarDados.errors, "status": "400"}

    def deletarUsuario(self, idUsuario: str) -> str:
        idUsuario = ObjectId(idUsuario)
        resultado = self.__colecao.delete_one({"_id": idUsuario})
        if resultado.deleted_count == 1:
            return {"mensagem": "Usuário removido com sucesso", "status": "200"}
        else:
            return {"mensagem": "Usuário não encontrado", "status": "404"}

    def atualizarUsuario(self, idUsuario: str, dadoUsuario: object) -> dict:
        idUsuario = ObjectId(idUsuario)
        if self.__validarDados.validate(dadoUsuario):
            try:
                self.__colecao.update_one({"_id": idUsuario}, {"$set": dadoUsuario})
                return {"mensagem": "Usuário atualizado", "status": "200"}
            except DuplicateKeyError:
                return {"mensagem": "CPF ou email já existem", "status": "409"}
        else:
            return {"mensagem": self.__validarDados.errors, "status": "404"}

    def getUsuario(self, idUsuario: str) -> dict:
        idUsuario = ObjectId(idUsuario)
        if resultado := self.__colecao.find_one({"_id": idUsuario}):
            return {
                "mensagem": resultado,
                "status": "200",
            }
        else:
            return {"mensagem": "Usuário não encontrado", "status": "404"}

    def getListaUsuarios(self) -> dict:
        return {"mensagem": list(self.__colecao.find()), "status": "200"}

    def getListaPetianos(self) -> dict:
        return {
            "mensagem": list(self.__colecao.find({"petiano": "petiano"})),
            "status": "200",
        }

    def getListaPetianosEgressos(self) -> dict:
        return {
            "mensagem": list(self.__colecao.find({"petiano": "petiano egresso"})),
            "status": "200",
        }

    def getIdUsuario(self, email: str) -> dict:
        if usuario := self.__colecao.find_one({"email": email}):
            return {
                "mensagem": usuario["_id"],
                "status": "200",
            }
        else:
            return {"mensagem": "Usuário não encontrado", "status": "404"}
