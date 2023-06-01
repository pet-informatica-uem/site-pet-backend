from pymongo import MongoClient
from app.models.validator.usuario import ValidarUsuario

class UsuarioBD():
    def __init__(self):
        cliente = MongoClient()
        db = cliente['petBD']
        self.__colecao = db['usuarios']
        self.__validarDados = ValidarUsuario().Usuario()

    def criarUsuario(self, dadoUsuario :object) -> str:
        if self.__validarDados.validate(dadoUsuario):
            self.__colecao.insert_one(dadoUsuario)
            return self.__colecao.find_one({'email': dadoUsuario['email']})['_id']
        else:
            return self.__validarDados.errors

    def detelarUsuario(self, idUsuario :str) -> str:
        if self.__colecao.find_one({'_id': idUsuario}):
            self.__colecao.delete_one({'_id': idUsuario})
            return "Usuário deletado"
        else:
            return "Usuário não encontrado"
        
    def setSenhaUsuario(self, idUsuario :str, senha :str) -> str:
        if self.__colecao.find_one({'_id': idUsuario}):
            self.__colecao.update_one({'_id': idUsuario}, {'$set': {'senha': senha}})
            return "Senha alterada"
        else: 
            return "Usuário não encontrado"
    
    def setCurso(self, idUsuario :str, curso :str) -> str:
        if self.__colecao.find_one({'_id': idUsuario}):
            self.__colecao.update_one({'_id': idUsuario}, {'$set': {'curso': curso}})
            return "Curso alterado"
        else:
            return "Usuário não encontrado"

    def setEstado(self, idUsuario :str, estado :str) -> str:
        if self.__colecao.find_one({'_id': idUsuario}):
            self.__colecao.update_one({'_id': idUsuario}, {'$set': {'estado': estado}})
            return "Estado alterado"
        else:
            return "Usuário não encontrado"

    def getIdUsuario(self, email :str) -> str:
        if self.__colecao.find_one({'email': email}):
            return self.__colecao.find_one({'email': email})['_id']
        else:
            return "Usuário não encontrado"
        
    def getSenha(self, idUsuario :str) -> str:
        if self.__colecao.find_one({'_id': idUsuario}):
            return self.__colecao.find_one({'_id': idUsuario})['senha']
        else:
            return "Usuário não encontrado"
        
    def getEstado(self, idUsuario :str) -> str:
        if self.__colecao.find_one({'_id': idUsuario}):
            return self.__colecao.find_one({'_id': idUsuario})['estado']
        else:
            return "Usuário não encontrado"
        
    def getUsuario(self, idUsuario :str) -> str:
        if self.__colecao.find_one({'_id': idUsuario}):
            return self.__colecao.find_one({'_id': idUsuario})
        else:
            return "Usuário não encontrado"
        
        


    


