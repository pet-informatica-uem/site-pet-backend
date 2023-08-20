import logging
from datetime import datetime

from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

from src.config import config
from src.modelos.autenticacao.autenticacao import TokenAutenticacao
from src.modelos.evento.evento import Evento
from src.modelos.excecao import JaExisteExcecao, NaoEncontradoExcecao
from src.modelos.inscrito.inscrito import Inscrito
from src.modelos.usuario.usuario import Petiano, TipoConta, Usuario

cliente: MongoClient = MongoClient(str(config.URI_BD))

colecaoTokens = cliente[config.NOME_BD]["authTokens"]

colecaoUsuarios = cliente[config.NOME_BD]["usuarios"]
colecaoUsuarios.create_index("email", unique=True)
colecaoUsuarios.create_index("cpf", unique=True)

colecaoEventos = cliente[config.NOME_BD]["eventos"]

colecaoInscritos = cliente[config.NOME_BD]["inscritos"]
colecaoInscritos.create_index([("idEvento", 1), ("idUsuario", 1)], unique=True)


class UsuarioBD:
    # operações banco de dados
    @staticmethod
    def criar(modelo: Usuario):
        # cria usuario no bd
        try:
            colecaoUsuarios.insert_one(modelo.model_dump(by_alias=True))
        except DuplicateKeyError:
            logging.error("Usuário já existe no banco de dados")
            raise JaExisteExcecao(mensagem="Usuário já existe no banco de dados")

    @staticmethod
    def buscar(indice: str, chave: str) -> Usuario:
        # Verifica se o usuário está cadastrado no bd
        if not colecaoUsuarios.find_one({indice: chave}):
            raise NaoEncontradoExcecao(mensagem="O Usuário não foi encontrado.")
        else:
            return Usuario(**colecaoUsuarios.find_one({indice: chave}))  # type: ignore

    @staticmethod
    def atualizar(modelo: Usuario):
        colecaoUsuarios.update_one({"_id": modelo.id}, {"$set": modelo.model_dump(by_alias=True)})

    @staticmethod
    def deletar(id: str):
        colecaoUsuarios.delete_one({"_id": id})

    @staticmethod
    def listar(petiano: bool = False) -> list[Usuario]:
        if not petiano:
            return [Usuario(**u) for u in colecaoUsuarios.find()]
        else:
            return [
                Usuario(**u)
                for u in colecaoUsuarios.find({"tipoConta": TipoConta.PETIANO})
            ]


class EventoBD:
    @staticmethod
    def criar(modelo: Evento):
        try:
            colecaoEventos.insert_one(modelo.model_dump(by_alias=True))
        except DuplicateKeyError:
            logging.error("Evento já existe no banco de dados")
            raise JaExisteExcecao(mensagem="Evento já existe no banco de dados")

    @staticmethod
    def buscar(indice: str, chave: str) -> Evento:
        # Verifica se o evento está cadastrado no bd
        if not colecaoEventos.find_one({indice: chave}):
            raise NaoEncontradoExcecao(mensagem="O evento não foi encontrado.")
        else:
            return Evento(**colecaoEventos.find_one({indice: chave}))  # type: ignore

    @staticmethod
    def atualizar(modelo: Evento):
        colecaoEventos.update_one({"_id": modelo.id}, {"$set": modelo.model_dump(by_alias=True)})

    @staticmethod
    def deletar(id: str):
        colecaoEventos.delete_one({"_id": id})

    @staticmethod
    def listar() -> list[Evento]:
        return [Evento(**e) for e in colecaoEventos.find()]


class InscritoBD:
    @staticmethod
    def criar(modelo: Inscrito):
        try:
            colecaoInscritos.insert_one(modelo.model_dump())
        except DuplicateKeyError:
            logging.error("Inscrito já existe no banco de dados")
            raise JaExisteExcecao(mensagem="Inscrito já existe no banco de dados")

    @staticmethod
    def buscar(idUsuario: str, idEvento: str) -> Inscrito:
        # Verifica se o inscrito está cadastrado no bd
        if not colecaoInscritos.find_one(
            {"idUsuario": idUsuario, "idEvento": idEvento}
        ):
            raise NaoEncontradoExcecao(mensagem="O inscrito não foi encontrado.")
        else:
            return Inscrito(**colecaoInscritos.find_one({"idUsuario": idUsuario, "idEvento": idEvento}))  # type: ignore

    @staticmethod
    def atualizar(modelo: Inscrito):
        colecaoInscritos.update_one(
            {"idUsuario": modelo.idUsuario, "idEvento": modelo.idEvento},
            {"$set": modelo.model_dump()},
        )

    @staticmethod
    def deletar(idUsuario: str, idEvento: str):
        colecaoInscritos.delete_one({"idUsuario": idUsuario, "idEvento": idEvento})

    @staticmethod
    def listarEventosUsuario(id: str) -> list[Inscrito]:
        return [Inscrito(**e) for e in colecaoInscritos.find({"idUsuario": id})]

    @staticmethod
    def listarInscritosEvento(id: str) -> list[Inscrito]:
        return [Inscrito(**e) for e in colecaoInscritos.find({"idEvento": id})]


class TokenAutenticacaoBD:
    @staticmethod
    def buscar(id: str) -> TokenAutenticacao:
        documento = colecaoTokens.find_one({"_id": id})
        if not documento:
            raise NaoEncontradoExcecao()

        return TokenAutenticacao(**documento)

    @staticmethod
    def deletar(id: str):
        resultado = colecaoTokens.delete_one({"_id": id})
        if resultado.deleted_count != 1:
            raise NaoEncontradoExcecao()

    @staticmethod
    def criar(id: str, idUsuario: str, validade: datetime) -> TokenAutenticacao:
        documento = {"_id": id, "idUsuario": idUsuario, "validade": validade}

        resultado = colecaoTokens.insert_one(documento)
        assert resultado.acknowledged

        return TokenAutenticacaoBD.buscar(str(resultado.inserted_id))

    @staticmethod
    def deletarTokensUsuario(idUsuario: str):
        colecaoTokens.delete_many({"idUsuario": idUsuario})
