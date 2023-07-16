from bson.objectid import ObjectId
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from src.modelos.exceptions import UsuarioJaExisteExcecao

from src.modelos.usuario.usuarioValidator import ValidarUsuario


class UsuarioBD:
    def __init__(self):
        cliente = MongoClient()
        db = cliente["petBD"]
        self.__colecao = db["usuarios"]
        self.__validarDados = ValidarUsuario().usuario()

    def criarUsuario(self, dadoUsuario: object) -> str:
        if self.__validarDados.validate(dadoUsuario):
            try:
                resultado = self.__colecao.insert_one(dadoUsuario)
                return str(resultado.inserted_id)
            except DuplicateKeyError as ex:
                raise UsuarioJaExisteExcecao(message="teste")
        else:
            raise Exception(self.__validarDados.errors)

    def deletarUsuario(self, idUsuario: str) -> dict:
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

    # recebe uma lista de IDs de usuários
    def getListaUsuarios(self, listaIdUsuarios: list) -> dict:
        listaIdUsuarios = [ObjectId(usuario) for usuario in listaIdUsuarios]
        if resultado := self.__colecao.find({"_id": {"$in": listaIdUsuarios}}):
            return {
                "mensagem": list(resultado),
                "status": "200",
            }
        else:
            return {"mensagem": "Algum usuário não foi encontrado", "status": "404"}

    def getTodosUsuarios(self) -> dict:
        return {"mensagem": list(self.__colecao.find()), "status": "200"}

    def getListaPetianos(self) -> dict:
        return {
            "mensagem": list(self.__colecao.find({"tipo conta": "petiano"})),
            "status": "200",
        }

    def getListaPetianosEgressos(self) -> dict:
        return {
            "mensagem": list(self.__colecao.find({"tipo conta": "petiano egresso"})),
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
