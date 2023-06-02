from pymongo import MongoClient
from app.models.validator.evento import ValidarEvento

class EventoBD():
    def __init__(self) -> None:
        cliente = MongoClient()
        db = cliente['petBD']
        self.__colecao = db['eventos']
        self.__validarDados = ValidarEvento().evento()

    def cadastrarEvento(self, dadosEvento :object) -> str:
        if self.__validarDados.validate(dadosEvento):
            self.__colecao.insert_one(dadosEvento)
            return 'Evento cadastrado com sucesso!'
        else:
            return self.__validarDados.errors
        
    def listarEventos(self) -> list:
        return list(self.__colecao.find({}, {'_id': 0}))
    
    def buscarEvento(self, nomeEvento :str) -> dict:
        return self.__colecao.find_one({'nome evento': nomeEvento}, {'_id': 0})         # se não achou retorna 0
    
    def atualizarEvento(self, nomeEvento :str, dadosEvento :object) -> str:
        if self.__validarDados.validate(dadosEvento):
            self.__colecao.update_one({'nome evento': nomeEvento}, {'$set': dadosEvento})
            return 'Evento atualizado com sucesso!'
        else:
            return self.__validarDados.errors
        
    def removerEvento(self, nomeEvento :str) -> str:
        self.__colecao.delete_one({'nome evento': nomeEvento})
        return 'Evento removido com sucesso!'
    