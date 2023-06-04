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
        
    def removerEvento(self, nomeEvento :str) -> str:
        self.__colecao.delete_one({'nome evento': nomeEvento})
        return 'Evento removido com sucesso!'
        
    def listarEventos(self) -> list:
        return list(self.__colecao.find({}, {'_id': 0}))
    
    def getEvento(self, nomeEvento :str) -> dict:
        return self.__colecao.find_one({'nome evento': nomeEvento}, {'_id': 0})
    
    def atualizarEvento(self, nomeEvento :str, dadosEvento :object) -> str:
        if self.__validarDados.validate(dadosEvento):
            self.__colecao.update_one({'nome evento': nomeEvento}, {'$set': dadosEvento})
            return 'Evento atualizado com sucesso!'
        else:
            return self.__validarDados.errors
    
    def buscarEvento(self, nomeEvento :str) -> dict:
        return self.__colecao.find_one({'nome evento': nomeEvento}, {'_id': 0})
    
    def getInscritos(self, nomeEvento :str) -> list:
        inscritos :dict = self.__colecao.find_one({'nome evento': nomeEvento}, {'inscritos': 1, '_id': 0})
        return inscritos['inscritos'] if inscritos else None
    
    def pushInscrito(self, nomeEvento :str, inscrito :str) -> str:
        self.__colecao.update_one({'nome evento': nomeEvento}, {'$push': {'inscritos': inscrito}})
        return 'Inscrito adicionado com sucesso!'
    
    # TODO testar daqui para baixo
    # TODO não remove o inscrito por algum motivo 
    def removerInscrito(self, nomeEvento: str, idUsuario: str) -> str:
        result = self.__colecao.update_one(
            {"nome evento": nomeEvento},
            {"$pull": {"inscritos": {"idUsuario": idUsuario}}},
        )
        if result.modified_count > 0:
            return "Inscrito removido com sucesso!"
        else:
            return "Não foi possível remover o inscrito."

    def getPresentes(self, nomeEvento :str) -> list:
        presentes :dict = self.__colecao.find_one({'nome evento': nomeEvento}, {'presentes': 1, '_id': 0})
        return presentes['presentes'] if presentes else None
    
    def pushPresente(self, nomeEvento :str, presente :str) -> str:
        self.__colecao.update_one({'nome evento': nomeEvento}, {'$push': {'presentes': presente}})
        return 'Presente adicionado com sucesso!'
    
    def removerPresente(self, nomeEvento: str, idUsuario: str) -> str:
        result = self.__colecao.update_one(
            {"nome evento": nomeEvento},
            {"$pull": {"presentes": {"idUsuario": idUsuario}}},
        )
        if result.modified_count > 0:
            return "Presente removido com sucesso!"
        else:
            return "Não foi possível remover o presente."
        
    

    
    
    