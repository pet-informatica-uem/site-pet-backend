from typing import Any

from bson.objectid import ObjectId
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

from modelos.excecao import (APIExcecaoBase, UsuarioJaExisteExcecao,
                             UsuarioNaoEncontradoExcecao)
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
            except DuplicateKeyError:
                raise UsuarioJaExisteExcecao()
        else:
            raise APIExcecaoBase(message="Erro de validação")

    def deletarUsuario(self, idUsuario: str) -> dict:
        idUsuario = ObjectId(idUsuario)
        resultado = self.__colecao.delete_one({"_id": idUsuario})
        if resultado.deleted_count:
            return True 
        
        raise UsuarioNaoEncontradoExcecao()

    def atualizarUsuario(self, idUsuario: str, dadoUsuario: object) -> None:
        idUsuario = ObjectId(idUsuario)
        if self.__validarDados.validate(dadoUsuario):
            try:
                self.__colecao.update_one({"_id": idUsuario}, {"$set": dadoUsuario})
            except DuplicateKeyError:
                raise UsuarioJaExisteExcecao()
        else:
            raise APIExcecaoBase(message="Erro de validação")

    def getUsuario(self, idUsuario: str) -> dict[str, Any]:
        idUsuario = ObjectId(idUsuario)
        if resultado := self.__colecao.find_one({"_id": idUsuario}):
            return resultado
        else:
            raise UsuarioNaoEncontradoExcecao()

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

    def getIdUsuario(self, email: str) -> str:
        if usuario := self.__colecao.find_one({"email": email}):
            return str(usuario["_id"])
        else:
            raise UsuarioNaoEncontradoExcecao()
