from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from app.model.validator.evento import ValidarEvento

class EventoBD():
    def __init__(self) -> None:
        cliente = MongoClient()
        db = cliente['petBD']
        self.__colecao = db['eventos']
        self.__validarDados = ValidarEvento().evento()

    # TODO o nome está como único, é necessária essa restrição?
    def cadastrarEvento(self, dadosEvento :object) -> str:
        if self.__validarDados.validate(dadosEvento):
            self.__colecao.insert_one(dadosEvento)
            return 'Evento cadastrado com sucesso!'
        else:
            return self.__validarDados.errors
        
    def removerEvento(self, nomeEvento :str) -> str:
        resultado = self.__colecao.delete_one({'nome evento': nomeEvento})
        if resultado.deleted_count:
            return {'mensagem': 'Evento removido com sucesso!', 'status': "200"}
        else:
            return {'mensagem': 'Evento não encontrado!', 'status': "404"}
           
        
    def listarEventos(self) -> list:
        return {'mensagem': list(self.__colecao.find({}, {'_id': 0})), 'status': "200"}
    
    def getEvento(self, nomeEvento :str) -> dict:
        return {'mensagem': self.__colecao.find_one({'nome evento': nomeEvento}, {'_id': 0}), 'status': "200"}
    
    def atualizarEvento(self, nomeEvento :str, dadosEvento :object) -> str:
        if self.__validarDados.validate(dadosEvento):
            try:
                self.__colecao.update_one({'nome evento': nomeEvento}, {'$set': dadosEvento})
                return {'mensagem': 'Evento atualizado com sucesso!', 'status': "200"}
            except DuplicateKeyError:
                return {'mensagem': 'Evento já cadastrado!', 'status': "409"}
        else:
            return {'mensagem': self.__validarDados.errors, 'status': "400"}
    
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
        
    

    
    
    