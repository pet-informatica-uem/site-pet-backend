import logging
from datetime import datetime

from pymongo.errors import DuplicateKeyError

from src.config import config
from src.modelos.autenticacao.autenticacao import TokenAutenticacao
from src.modelos.evento.evento import Evento
from src.modelos.excecao import JaExisteExcecao, NaoEncontradoExcecao
from src.modelos.inscrito.inscrito import Inscrito
from src.modelos.usuario.usuario import Petiano, TipoConta, Usuario
from src.modelos.conexao import ConexaoBD


class UsuarioBD(ConexaoBD):
    def __init__(self) -> None:
        super().__init__(config.NOME_BD)

    # cria usuario no bd
    def criar(self, modelo: Usuario):
        try:
            self.colecaoUsuarios.insert_one(modelo.model_dump(by_alias=True))
        except DuplicateKeyError:
            logging.error("Usuário já existe no banco de dados")
            raise JaExisteExcecao(message="Usuário já existe no banco de dados")

    # Verifica se o usuário está cadastrado no bd
    def buscar(self, indice: str, chave: str) -> Usuario:
        if not self.colecaoUsuarios.find_one({indice: chave}):
            raise NaoEncontradoExcecao(message="O Usuário não foi encontrado.")
        else:
            return Usuario(**self.colecaoUsuarios.find_one({indice: chave}))  # type: ignore

    def atualizar(self, modelo: Usuario):
        self.colecaoUsuarios.update_one(
            {"_id": modelo.id}, {"$set": modelo.model_dump(by_alias=True)}
        )

    def deletar(self, id: str):
        self.colecaoUsuarios.delete_one({"_id": id})

    def listar(self, petiano: bool = False) -> list[Usuario]:
        if not petiano:
            return [Usuario(**u) for u in self.colecaoUsuarios.find()]
        else:
            return [
                Usuario(**u)
                for u in self.colecaoUsuarios.find({"tipoConta": TipoConta.PETIANO})
            ]


class EventoBD(ConexaoBD):
    def __init__(self) -> None:
        super().__init__(config.NOME_BD)

    def criar(self, modelo: Evento):
        try:
            self.colecaoEventos.insert_one(modelo.model_dump(by_alias=True))
        except DuplicateKeyError:
            logging.error("Evento já existe no banco de dados")
            raise JaExisteExcecao(message="Evento já existe no banco de dados")

    def buscar(self, indice: str, chave: str) -> Evento:
        # Verifica se o evento está cadastrado no bd
        if not self.colecaoEventos.find_one({indice: chave}):
            raise NaoEncontradoExcecao(message="O evento não foi encontrado.")
        else:
            return Evento(**self.colecaoEventos.find_one({indice: chave}))  # type: ignore

    def atualizar(self, modelo: Evento):
        self.colecaoEventos.update_one(
            {"_id": modelo.id}, {"$set": modelo.model_dump(by_alias=True)}
        )

    def deletar(self, id: str):
        self.colecaoEventos.delete_one({"_id": id})

    def listar(self) -> list[Evento]:
        return [Evento(**e) for e in self.colecaoEventos.find()]


class InscritoBD(ConexaoBD):
    def __init__(self) -> None:
        super().__init__(config.NOME_BD)

    def criar(self, modelo: Inscrito):
        try:
            self.colecaoInscritos.insert_one(modelo.model_dump())
        except DuplicateKeyError:
            logging.error("Inscrito já existe no banco de dados")
            raise JaExisteExcecao(message="Inscrito já existe no banco de dados")

    def buscar(self, idEvento: str, idUsuario: str) -> Inscrito:
        # Verifica se o inscrito está cadastrado no bd
        if inscrito := self.colecaoInscritos.find_one(
            {"idEvento": idEvento, "idUsuario": idUsuario}
        ):
            return Inscrito(**inscrito)  # type: ignore
        else:
            print(inscrito)
            raise NaoEncontradoExcecao(message="O inscrito não foi encontrado.")

    def atualizar(self, modelo: Inscrito):
        self.colecaoInscritos.update_one(
            {"idEvento": modelo.idEvento, "idUsuario": modelo.idUsuario},
            {"$set": modelo.model_dump()},
        )

    def deletar(self, idEvento: str, idUsuario: str):
        self.colecaoInscritos.delete_one({"idEvento": idEvento, "idUsuario": idUsuario})

    def listarEventosUsuario(self, id: str) -> list[Inscrito]:
        return [Inscrito(**e) for e in self.colecaoInscritos.find({"idUsuario": id})]

    def listarInscritosEvento(self, id: str) -> list[Inscrito]:
        return [Inscrito(**e) for e in self.colecaoInscritos.find({"idEvento": id})]


class TokenAutenticacaoBD(ConexaoBD):
    def __init__(self) -> None:
        super().__init__(config.NOME_BD)

    def buscar(self, id: str) -> TokenAutenticacao:
        documento = self.colecaoTokens.find_one({"_id": id})
        if not documento:
            raise NaoEncontradoExcecao()

        return TokenAutenticacao(**documento)

    def deletar(self, id: str):
        resultado = self.colecaoTokens.delete_one({"_id": id})
        if resultado.deleted_count != 1:
            raise NaoEncontradoExcecao()

    def criar(self, id: str, idUsuario: str, validade: datetime) -> TokenAutenticacao:
        documento = {"_id": id, "idUsuario": idUsuario, "validade": validade}

        resultado = self.colecaoTokens.insert_one(documento)
        assert resultado.acknowledged

        return TokenAutenticacaoBD.buscar(str(resultado.inserted_id))

    def deletarTokensUsuario(self, idUsuario: str):
        self.colecaoTokens.delete_many({"idUsuario": idUsuario})
