from pymongo import MongoClient
from app.model.validator.usuario import ValidarUsuario


class UsuarioBD:
    def __init__(self):
        cliente = MongoClient()
        db = cliente["petBD"]
        self.__colecao = db["usuarios"]
        self.__validarDados = ValidarUsuario().usuario()

    def criarUsuario(self, dadoUsuario: object) -> str:
        if self.__validarDados.validate(dadoUsuario):
            self.__colecao.insert_one(dadoUsuario)
            return self.__colecao.find_one({"email": dadoUsuario["email"]})["_id"]
        else:
            return self.__validarDados.errors

    def deletarUsuario(self, idUsuario: str) -> str:
        if self.__colecao.find_one({"_id": idUsuario}):
            self.__colecao.delete_one({"_id": idUsuario})
            return "Usuário deletado"
        else:
            return "Usuário não encontrado"
        
    def atualizarUsuario(self, idUsuario: str, dadoUsuario: object) -> str:
        if self.__colecao.find_one({"_id": idUsuario}):
            self.__colecao.update_one({"_id": idUsuario}, {"$set": dadoUsuario})
            return "Usuário atualizado"
        else:
            return "Usuário não encontrado"
        
    def getUsuario(self, idUsuario: str) -> str:
        if self.__colecao.find_one({"_id": idUsuario}):
            return self.__colecao.find_one({"_id": idUsuario})
        else:
            return "Usuário não encontrado"
        
    def getListaUsuarios(self) -> list:
        return list(self.__colecao.find())
        
    def getListaPetianos(self) -> list:
        return list(self.__colecao.find({"petiano": "petiano"}))
    
    def getListaPetianosEgressos(self) -> list:
        return list(self.__colecao.find({"petiano": "petiano egresso"}))

    def getIdUsuario(self, email: str) -> str:
        if self.__colecao.find_one({"email": email}):
            return self.__colecao.find_one({"email": email})["_id"]
        else:
            return "Usuário não encontrado"
