from pymongo import MongoClient
from datetime import datetime, timedelta
from random import randint
from app.model.validator.recuperarSenha import ValidarRecuperacaoSenha

class RecuperarSenha():
    def __init__(self):
        cliente = MongoClient()
        db = cliente["petBD"]
        self.__colecao = db["recuperarSenha"]
        self.__validarDados = ValidarRecuperacaoSenha().usuario()

    def criarCodigo(self, idUsuario :str) -> dict:
        self.__colecao.find_one_and_delete({"idUsuario": idUsuario})
        self.__colecao.insert_one({"idUsuario": idUsuario, "codigo": self.__gerarCodigo(), "data criacao": datetime.now()})
        return {'mensagem': 'Código criado com sucesso', 'status': "200"}
    
    def getCodigoUsuario(self, idUsuario :str) -> dict:
        usuario = self.__colecao.find_one({"idUsuario": idUsuario})
        if usuario:
            if (usuario['data criacao'] + timedelta(minutes=3)) < datetime.now():
                self.__colecao.find_one_and_delete({"idUsuario": idUsuario})
                return {'mensagem': 'Código expirado', 'status': "404"}
            return {'mensagem': usuario['codigo'], 'status': "200"}
        return {'mensagem': 'Usuário não encontrado', 'status': "404"}
    
    def __gerarCodigo(self) -> str:
        codigo = ''
        for i in range(4):
            codigo += str(randint(0, 9))
        return codigo