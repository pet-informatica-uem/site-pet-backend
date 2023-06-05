from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from app.model.validator.usuario import ValidarUsuario


class UsuarioBD:
    def __init__(self):
        cliente = MongoClient()
        db = cliente["petBD"]
        self.__colecao = db["usuarios"]
        self.__validarDados = ValidarUsuario().usuario()

    def criarUsuario(self, dadoUsuario: object) -> str:
        if self.__validarDados.validate(dadoUsuario):
            try:
                self.__colecao.insert_one(dadoUsuario)
                return {
                    "mensagem": self.getIdUsuario(dadoUsuario["email"])['mensagem'],
                    "status": "200",
                }
            except DuplicateKeyError:
                return {"mensagem": "CPF ou email já existem", "status": "400"}
        else:
            return {"mensagem": self.__validarDados.errors, "status": "400"}

    def deletarUsuario(self, idUsuario: str) -> str:
        if self.__colecao.find_one({"_id": idUsuario}):
            self.__colecao.delete_one({"_id": idUsuario})
            return {"mensagem": "Usuário deletado", "status": "200"}
        else:
            return {"mensagem": "Usuário não encontrado", "status": "404"}

    def atualizarUsuario(self, idUsuario: str, dadoUsuario: object) -> dict:
        if self.__colecao.find_one({"_id": idUsuario}):
            self.__colecao.update_one({"_id": idUsuario}, {"$set": dadoUsuario})
            return {"mensagem": "Usuário atualizado", "status": "200"}
        else:
            return {"mensagem": "Usuário não encontrado", "status": "404"}

    def getUsuario(self, idUsuario: str) -> dict:
        if self.__colecao.find_one({"_id": idUsuario}):
            return {
                "mensagem": self.__colecao.find_one({"_id": idUsuario}),
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
