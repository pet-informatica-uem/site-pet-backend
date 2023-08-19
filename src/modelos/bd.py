import logging
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from src.modelos.evento.evento import Evento
from src.modelos.excecao import (
    APIExcecaoBase,
    NaoEncontradoExcecao,
    JaExisteExcecao,
)
from src.modelos.usuario.usuario import TipoConta, Usuario, Petiano


from src.config import config

cliente: MongoClient = MongoClient(str(config.URI_BD))

colecaoTokens = cliente[config.NOME_BD]["authTokens"]

colecaoUsuarios = cliente[config.NOME_BD]["usuarios"]
colecaoUsuarios.create_index("email", unique=True)
colecaoUsuarios.create_index("cpf", unique=True)

colecaoEventos = cliente[config.NOME_BD]["eventos"]

colecaoInscritos = cliente[config.NOME_BD]["inscritos"]



class UsuarioBD:
    # operações banco de dados
    @staticmethod
    def buscar(indice: str, chave: str) -> Usuario:
        # Verifica se o usuário está cadastrado no bd
        if not colecaoUsuarios.find_one({indice: chave}):
            raise NaoEncontradoExcecao(mensagem="O Usuário não foi encontrado.")
        else:
            return Usuario(**colecaoUsuarios.find_one({indice: chave}))  # type: ignore

    @staticmethod
    def criar(modelo: Usuario):
        # cria usuario no bd
        try:
            colecaoUsuarios.insert_one(modelo.model_dump(by_alias=True))
        except DuplicateKeyError:
            logging.error("Usuário já existe no banco de dados")
            raise JaExisteExcecao(mensagem="Usuário já existe no banco de dados")

    @staticmethod
    def atualizar(modelo: Usuario):
        colecaoUsuarios.update_one({"_id": modelo.id}, modelo.model_dump(by_alias=True))

    @staticmethod
    def deletar(id: str):
        colecaoUsuarios.delete_one({"_id": id})

    @staticmethod
    def listar(petiano: bool = False) -> list[Usuario] | list[Petiano]:
        if not petiano:
            return [Usuario(**u) for u in colecaoUsuarios.find()]
        else:
            return [
                Usuario(**u)
                for u in colecaoUsuarios.find({"tipoConta": TipoConta.PETIANO})
            ]


class EventoBD:
    @staticmethod
    def buscar(indice: str, chave: str) -> Evento:
        # Verifica se o evento está cadastrado no bd
        if not colecaoEventos.find_one({indice: chave}):
            raise NaoEncontradoExcecao(mensagem="O evento não foi encontrado.")
        else:
            return Evento(**colecaoEventos.find_one({indice: chave}))  # type: ignore

    @staticmethod
    def criar(modelo: Evento):
        try:
            colecaoEventos.insert_one(modelo.model_dump(by_alias=True))
        except DuplicateKeyError:
            logging.error("Evento já existe no banco de dados")
            raise JaExisteExcecao(mensagem="Evento já existe no banco de dados")

    @staticmethod
    def atualizar(modelo: Evento):
        colecaoEventos.update_one({"_id": modelo.id}, modelo.model_dump(by_alias=True))

    @staticmethod
    def deletar(id: str):
        colecaoEventos.delete_one({"_id": id})

    @staticmethod
    def listar() -> list[Evento]:
        return [Evento(**e) for e in colecaoEventos.find()]
    

class InscritoBD:
    def 
