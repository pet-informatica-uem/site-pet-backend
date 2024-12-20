"""
Classes que encapsulam operações de banco de dados.
"""

import logging
from datetime import datetime

from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

from src.config import config
from src.modelos.autenticacao.autenticacao import TokenAutenticacao
from src.modelos.evento.evento import Evento, Inscrito, TipoVaga
from src.modelos.evento.intervaloBusca import IntervaloBusca
from src.modelos.excecao import APIExcecaoBase, JaExisteExcecao, NaoEncontradoExcecao
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

colecaoRegistro = cliente[config.NOME_BD]["registros"]


class UsuarioBD:
    """
    Encapsula operações do banco de dados de usuários.
    """

    # operações banco de dados
    @staticmethod
    def criar(modelo: Usuario):
        """
        Cria um usuário no banco de dados.

        :param modelo: Usuário a ser criado.
        :raises JaExisteExcecao: Caso um usuário com o mesmo email ou CPF já exista no banco de dados.
        """
        # cria usuario no bd
        try:
            colecaoUsuarios.insert_one(modelo.model_dump(by_alias=True))
        except DuplicateKeyError:
            logging.error("Usuário já existe no banco de dados")
            raise JaExisteExcecao(message="Usuário já existe no banco de dados")

    @staticmethod
    def buscar(campo: str, valor: str) -> Usuario:
        """
        Busca um usuário no banco de dados de acordo com o índice e a valor fornecidos.

        :param campo: Campo de busca.
        :param valor: Valor de busca.
        :return: Primeiro usuário encontrado com um campo com valor igual ao fornecido.
        """
        # Verifica se o usuário está cadastrado no bd
        if not colecaoUsuarios.find_one({campo: valor}):
            raise NaoEncontradoExcecao(message="O Usuário não foi encontrado.")
        else:
            return Usuario(**colecaoUsuarios.find_one({campo: valor}))  # type: ignore

    @staticmethod
    def atualizar(modelo: Usuario):
        """
        Atualiza um usuário no banco de dados.

        :param modelo: Usuário a ser atualizado.
        """
        colecaoUsuarios.update_one(
            {"_id": modelo.id}, {"$set": modelo.model_dump(by_alias=True)}
        )

    @staticmethod
    def deletar(id: str):
        """
        Deleta um usuário do banco de dados.

        :param id: Identificador do usuário a ser deletado.
        """
        colecaoUsuarios.delete_one({"_id": id})

    @staticmethod
    def listar() -> list[Usuario]:
        """
        Retorna uma lista com todos os usuários cadastrados no banco de dados.

        :return usuarios: Lista com todos os usuários cadastrados no banco de dados.
        """
        return [Usuario(**u) for u in colecaoUsuarios.find()]

    @staticmethod
    def listarPetianos() -> list[Usuario]:
        """
        Retorna uma lista com todos os petianos cadastrados no banco de dados.

        :return petianos: Lista com todos os petianos cadastrados no banco de dados.
        """
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
        evento = colecaoEventos.find_one({indice: chave})
        if not evento:
            raise NaoEncontradoExcecao(message="O evento não foi encontrado.")
        else:
            #return Evento(**evento).model_dump(by_alias=True)  # type: ignore
            print(evento)
            return Evento(**evento)  # type: ignore 

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

        #print(query) 
        #print("*"*50)

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

        #print(resultadoBusca)

        resultado = [Evento(**e) for e in resultadoBusca]
        return resultado

    @staticmethod
    def criarInscrito(id_evento: str, inscrito: Inscrito):
        try:
            # Busca o evento pelo id
            evento = colecaoEventos.find_one({"_id": id_evento})
            
            if not evento:
                raise Exception("Evento não encontrado")

            # Verifica se o usuário já está inscrito
            for i in evento.get("inscritos", []):
                if i["idUsuario"] == inscrito.idUsuario:
                    logging.error("Inscrito já existe no evento")
                    raise JaExisteExcecao(message="Inscrito já existe no evento")

            # Adiciona o novo inscrito à lista de inscritos do evento
            novo_inscrito = inscrito.model_dump()

            # Atualiza o documento no MongoDB
            update_result = colecaoEventos.update_one(
                {"_id": id_evento},
                {
                    "$push": {"inscritos": novo_inscrito},
                    "$inc": {
                        "vagasDisponiveisComNote": -1
                        if inscrito.tipoVaga == TipoVaga.COM_NOTE
                        else 0,
                        "vagasDisponiveisSemNote": -1
                        if inscrito.tipoVaga == TipoVaga.SEM_NOTE
                        else 0,
                    },
                }
            )

            if update_result.modified_count == 0:
                raise Exception("Falha ao atualizar o evento com o novo inscrito.")

        except DuplicateKeyError:
            logging.error("Inscrito já existe no evento")
            raise JaExisteExcecao(message="Inscrito já existe no evento")
        except Exception as e:
            logging.error(f"Erro inesperado: {str(e)}")
            raise

    @staticmethod
    def buscarInscrito(idEvento: str, idUsuario: str) -> Inscrito:
        evento = colecaoEventos.find_one({"_id": idEvento})
        if not evento:
            raise NaoEncontradoExcecao(message="Evento não encontrado")
        for inscrito_data in evento.get("inscritos", []):
            if inscrito_data["idUsuario"] == idUsuario:
                return Inscrito(**inscrito_data)
        raise NaoEncontradoExcecao(message="O inscrito não foi encontrado.")

    @staticmethod
    def deletarInscrito(idEvento: str, idUsuario: str):
        resultado = colecaoEventos.update_one(
            {"_id": idEvento},
            {"$pull": {"inscritos": {"idUsuario": idUsuario}}}
        )
        if resultado.modified_count == 0:
            raise NaoEncontradoExcecao(message="O inscrito não foi encontrado para remoção.")

    @staticmethod
    def listarInscritosEvento(idEvento: str) -> list[Inscrito]:
        evento = colecaoEventos.find_one({"_id": idEvento})
        if not evento:
            raise NaoEncontradoExcecao(message="Evento não encontrado")
        inscritos_data = evento.get("inscritos", [])
        return [Inscrito(**inscrito) for inscrito in inscritos_data]

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
            return [
                RegistroLogin(**r)
                for r in colecaoRegistro.find({"emailUsuario": email})
            ]  # type: ignore

    @staticmethod
    def listarTodos() -> list[RegistroLogin]:
        """
        Lista todos os registros de login.
        """
        return [RegistroLogin(**r) for r in colecaoRegistro.find()]
