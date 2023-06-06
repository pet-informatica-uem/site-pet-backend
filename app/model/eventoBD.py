from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from datetime import datetime
from app.model.validator.evento import ValidarEvento

class EventoBD():
    def __init__(self) -> None:
        cliente = MongoClient()
        db = cliente['petBD']
        self.__colecao = db['eventos']
        self.__validarEvento = ValidarEvento().evento()

    def cadastrarEvento(self, dadosEvento :object) -> str:
        if self.__validarEvento.validate(dadosEvento):
            try:
                self.__colecao.insert_one(dadosEvento)
                return {'mensagem': 'Evento cadastrado com sucesso!', 'status': '200'}
            except DuplicateKeyError:
                return {'mensagem': 'Evento já cadastrado!', 'status': '409'}
        else:
            return {'mensagem': self.__validarEvento.errors, 'status': '400'}
        
    def removerEvento(self, nomeEvento :str) -> str:
        resultado = self.__colecao.delete_one({'nome evento': nomeEvento})
        if resultado.deleted_count == 1:
            return {'mensagem': 'Evento removido com sucesso!', 'status': "200"}
        else:
            return {'mensagem': 'Evento não encontrado!', 'status': "404"}
           
    def listarEventos(self) -> list:
        return {'mensagem': list(self.__colecao.find({}, {'_id': 0})), 'status': "200"}
        
    def atualizarEvento(self, nomeEvento :str, dadosEvento :object) -> str:
        if self.__validarEvento.validate(dadosEvento):
            try:
                self.__colecao.update_one({'nome evento': nomeEvento}, {'$set': dadosEvento})
                return {'mensagem': 'Evento atualizado com sucesso!', 'status': "200"}
            except DuplicateKeyError:
                return {'mensagem': 'Evento já cadastrado!', 'status': "409"}
        else:
            return {'mensagem': self.__validarEvento.errors, 'status': "400"}
        
    def getEvento(self, nomeEvento :str) -> dict:
        resultado = self.__colecao.find_one({'nome evento': nomeEvento})
        if resultado:
            return {'mensagem': resultado, 'status': "200"}
        else:
            return {'mensagem': 'Evento não encontrado!', 'status': "404"}
    
    def addInscrito(self, nomeEvento :str, idUsuario :str) -> str:
        evento = self.getEvento(nomeEvento)
        if evento['status'] == '404':
            return {'mensagem': 'Evento não encontrado!', 'status': "404"}
        
        usuariosInscritos = evento['mensagem']['inscritos']
        if any(idUsuario == usuario['idUsuario'] for usuario in usuariosInscritos):
            return {'mensagem': 'Inscrito já cadastrado!', 'status': "409"}
        else:
            self.__colecao.update_one({'nome evento': nomeEvento}, {'$push': {'inscritos': {'idUsuario': idUsuario, 'data/hora': datetime.now()}}})
            return {'mensagem': 'Inscrito adicionado com sucesso!', 'status': "200"}
    
    def removerInscrito(self, nomeEvento: str, idUsuario: str) -> str:
        result = self.__colecao.update_one(
            {"nome evento": nomeEvento},
            {"$pull": {"inscritos": {"idUsuario": idUsuario}}},
        )
        if result.modified_count > 0:
            return {'mensagem': 'Inscrito removido com sucesso!', 'status': "200"}
        else:
            return {'mensagem': 'Não foi possível remover o inscrito.', 'status': "404"}

    # TODO testar daqui para baixo
    # saber se a pessoa já está inscrita no evento
    def addPresente(self, nomeEvento :str, idUsuario :str) -> str:    
        evento = self.getEvento(nomeEvento)
        if evento['status'] == '404':
            return {'mensagem': 'Evento não encontrado!', 'status': "404"}
        
        usuariosPresentes = evento['mensagem']['presentes']
        if any(idUsuario == usuario['idUsuario'] for usuario in usuariosPresentes):
            return {'mensagem': 'Inscrito já cadastrado!', 'status': "409"}
        else:
            self.__colecao.update_one({'nome evento': nomeEvento}, {'$push': {'inscritos': {'idUsuario': idUsuario, 'data/hora': datetime.now()}}})
            return {'mensagem': 'Inscrito adicionado com sucesso!', 'status': "200"}
    
    def getPresentes(self, nomeEvento :str) -> list:
        presentes :dict = self.__colecao.find_one({'nome evento': nomeEvento}, {'presentes': 1, '_id': 0})
        return presentes['presentes'] if presentes else None
    
    def removerPresente(self, nomeEvento: str, idUsuario: str) -> str:
        result = self.__colecao.update_one(
            {"nome evento": nomeEvento},
            {"$pull": {"presentes": {"idUsuario": idUsuario}}},
        )
        if result.modified_count > 0:
            return "Presente removido com sucesso!"
        else:
            return "Não foi possível remover o presente."
        
    

    
    
    