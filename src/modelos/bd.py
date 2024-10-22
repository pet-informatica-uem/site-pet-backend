import logging
from datetime import datetime

from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

from src.config import config
from src.modelos.autenticacao.autenticacao import TokenAutenticacao
from src.modelos.evento.evento import Evento
from src.modelos.evento.intervaloBusca import IntervaloBusca
from src.modelos.excecao import APIExcecaoBase, JaExisteExcecao, NaoEncontradoExcecao
from src.modelos.inscrito.inscrito import Inscrito
from src.modelos.registro.registroLogin import RegistroLogin
from src.modelos.usuario.usuario import Petiano, TipoConta, Usuario

cliente: MongoClient = MongoClient(str(config.URI_BD))

if config.MOCK_BD:
    config.NOME_BD = "petBD-test"
    cliente.drop_database(config.NOME_BD)

colecaoTokens = cliente[config.NOME_BD]["authTokens"]

colecaoUsuarios = cliente[config.NOME_BD]["usuarios"]
colecaoUsuarios.create_index("email", unique=True)
colecaoUsuarios.create_index("cpf", unique=True)

colecaoEventos = cliente[config.NOME_BD]["eventos"]
colecaoEventos.create_index("titulo", unique=True)

colecaoInscritos = cliente[config.NOME_BD]["inscritos"]
colecaoInscritos.create_index([("idEvento", 1), ("idUsuario", 1)], unique=True)

colecaoRegistro = cliente[config.NOME_BD]["registros"]


class UsuarioBD:
    # operações banco de dados
    @staticmethod
    def criar(modelo: Usuario):
        # cria usuario no bd
        try:
            colecaoUsuarios.insert_one(modelo.model_dump(by_alias=True))
        except DuplicateKeyError:
            logging.error("Usuário já existe no banco de dados")
            raise JaExisteExcecao(message="Usuário já existe no banco de dados")

    @staticmethod
    def buscar(indice: str, chave: str) -> Usuario:
        # Verifica se o usuário está cadastrado no bd
        if not colecaoUsuarios.find_one({indice: chave}):
            raise NaoEncontradoExcecao(message="O Usuário não foi encontrado.")
        else:
            return Usuario(**colecaoUsuarios.find_one({indice: chave}))  # type: ignore

    @staticmethod
    def atualizar(modelo: Usuario):
        colecaoUsuarios.update_one(
            {"_id": modelo.id}, {"$set": modelo.model_dump(by_alias=True)}
        )

    @staticmethod
    def deletar(id: str):
        colecaoUsuarios.delete_one({"_id": id})

    @staticmethod
    def listar() -> list[Usuario]:
        return [Usuario(**u) for u in colecaoUsuarios.find()]

    @staticmethod
    def listarPetianos() -> list[Usuario]:
        return [
            Usuario(**u) for u in colecaoUsuarios.find({"tipoConta": TipoConta.PETIANO})
        ]


class EventoBD:
    @staticmethod
    def criar(modelo: Evento):
        try:
            colecaoEventos.insert_one(modelo.model_dump(by_alias=True))
        except DuplicateKeyError as e:
            logging.error("Evento já existe no banco de dados" + str(e))
            raise JaExisteExcecao(message="Evento já existe no banco de dados")

    @staticmethod
    def buscar(indice: str, chave: str) -> Evento:
        # Verifica se o evento está cadastrado no bd
        if not colecaoEventos.find_one({indice: chave}):
            raise NaoEncontradoExcecao(message="O evento não foi encontrado.")
        else:
            return Evento(**colecaoEventos.find_one({indice: chave}))  # type: ignore

    @staticmethod
    def atualizar(modelo: Evento):
        try:
            colecaoEventos.update_one(
                {"_id": modelo.id}, {"$set": modelo.model_dump(by_alias=True)}
            )
        except DuplicateKeyError:
            logging.error("Evento já existe no banco de dados")
            raise JaExisteExcecao(
                message="Já existe um evento com esse título no banco de dados"
            )

    @staticmethod
    def deletar(id: str):
        colecaoEventos.delete_one({"_id": id})

    @staticmethod
    def listar(query: IntervaloBusca) -> list[Evento]:
        resultado: list[Evento]

        if query == IntervaloBusca.PASSADO:
            dbQuery = {"fimEvento": {"$lt": datetime.now()}}
            resultadoBusca = colecaoEventos.find(dbQuery)
        elif query == IntervaloBusca.PRESENTE:
            dbQuery = {
                "inicioEvento": {"$lt": datetime.now()},
                "fimEvento": {"$gt": datetime.now()},
            }
            resultadoBusca = colecaoEventos.find(dbQuery)
        elif query == IntervaloBusca.FUTURO:
            dbQuery = {"inicioEvento": {"$gt": datetime.now()}}
            resultadoBusca = colecaoEventos.find(dbQuery)
        else:
            resultadoBusca = colecaoEventos.find()

        resultado = [Evento(**e) for e in resultadoBusca]
        return resultado


class InscritoBD:
    @staticmethod
    def criar(modelo: Inscrito):
        try:
            colecaoInscritos.insert_one(modelo.model_dump())
        except DuplicateKeyError:
            logging.error("Inscrito já existe no banco de dados")
            raise JaExisteExcecao(message="Inscrito já existe no banco de dados")

    # @staticmethod
    # def criar(inscrito: Inscrito, evento: Evento, usuario: Usuario) -> None:
    #     """Cria um inscrito no banco de dados.

    #     - inscrito -- inscrito a ser cadastrado
    #     - evento -- evento a ser atualizado
    #     - usuario -- usuário a ser atualizado

    #     Return: None
    #     """

    #     session = cliente.start_session()

    #     # Realiza as operações no BD usando uma transação
    #     try:
    #         session.start_transaction()

    #         InscritoBD._criar(inscrito)
    #         EventoBD.atualizar(evento)
    #         UsuarioBD.atualizar(usuario)

    #         # Commita as operações
    #         session.commit_transaction()
    #     except Exception as e:
    #         logging.error(f"Erro ao inscrever usuário em {evento.titulo}. Erro: {str(e)}")

    #         # Aborta a transação
    #         session.abort_transaction()
    #         raise APIExcecaoBase(message="Erro ao criar inscrito")

    @staticmethod
    def buscar(idEvento: str, idUsuario: str) -> Inscrito:
        # Verifica se o inscrito está cadastrado no bd
        if inscrito := colecaoInscritos.find_one(
            {"idEvento": idEvento, "idUsuario": idUsuario}
        ):
            return Inscrito(**inscrito)  # type: ignore
        else:
            raise NaoEncontradoExcecao(message="O inscrito não foi encontrado.")

    @staticmethod
    def atualizar(modelo: Inscrito):
        colecaoInscritos.update_one(
            {"idEvento": modelo.idEvento, "idUsuario": modelo.idUsuario},
            {"$set": modelo.model_dump()},
        )

    @staticmethod
    def deletar(idEvento: str, idUsuario: str):
        colecaoInscritos.delete_one({"idEvento": idEvento, "idUsuario": idUsuario})

    @staticmethod
    def listarEventosUsuario(id: str) -> list[Inscrito]:
        return [Inscrito(**e) for e in colecaoInscritos.find({"idUsuario": id})]

    @staticmethod
    def listarInscritosEvento(id: str) -> list[Inscrito]:
        return [Inscrito(**e) for e in colecaoInscritos.find({"idEvento": id})]


class TokenAutenticacaoBD:
    """
    Encapsula operações do banco de dados de tokens de autenticação.
    """
    @staticmethod
    def buscar(id: str) -> TokenAutenticacao:
        """
        Busca um token de autenticação pelo id `id` no banco de dados e o retorna, caso exista.
        
        :param id: Identificador do token.
        :return: Token de autenticação.
        :raises NaoEncontradoExcecao: Caso o token não seja encontrado.
        """
        documento = colecaoTokens.find_one({"_id": id})
        if not documento:
            raise NaoEncontradoExcecao()

        return TokenAutenticacao(**documento)

    @staticmethod
    def deletar(id: str):
        """
        Deleta o token de autenticação de id `id` do banco de dados.

        :param id: Identificador do token.
        :raises NaoEncontradoExcecao: Caso o token não seja encontrado.
        """
        resultado = colecaoTokens.delete_one({"_id": id})
        if resultado.deleted_count != 1:
            raise NaoEncontradoExcecao()

    @staticmethod
    def criar(id: str, idUsuario: str, validade: datetime) -> TokenAutenticacao:
        """
        Cria um token de autenticação com id `id` no banco de dados.
        O token é associado ao usuário de id `idUsuario` e é válido até `validade`.

        :param id: Identificador do token.
        :param idUsuario: Identificador do usuário associado ao token.
        :param validade: Data de validade do token.
        :return: Token de autenticação criado.
        """
        documento = {"_id": id, "idUsuario": idUsuario, "validade": validade}

        resultado = colecaoTokens.insert_one(documento)
        assert resultado.acknowledged

        return TokenAutenticacaoBD.buscar(str(resultado.inserted_id))

    @staticmethod
    def deletarTokensUsuario(idUsuario: str):
        """
        Remove todos os tokens de autenticação do usuário com id `idUsuario`.

        :param idUsuario: Identificador do usuário.
        """
        colecaoTokens.delete_many({"idUsuario": idUsuario})


class RegistroLoginBD:
    @staticmethod
    def criar(modelo: RegistroLogin):
        """
        Cria um registro de login no banco de dados.
        """
        colecaoRegistro.insert_one(modelo.model_dump())

    @staticmethod
    def listarRegistrosUsuario(email: str) -> list[RegistroLogin]:
        """
        Lista os registros de login de um usuário.
        """
        # Verifica se o email possui algum registro associado
        if not colecaoRegistro.find_one({"emailUsuario": email}):
            raise NaoEncontradoExcecao(message="Nenhum registro encontrado.")
        else:
            return [RegistroLogin(**r) for r in colecaoRegistro.find({"emailUsuario": email})]  # type: ignore

    @staticmethod
    def listarTodos() -> list[RegistroLogin]:
        """
        Lista todos os registros de login.
        """
        return [RegistroLogin(**r) for r in colecaoRegistro.find()]
