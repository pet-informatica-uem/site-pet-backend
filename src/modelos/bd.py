import logging
from datetime import datetime

from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

from src.config import config
from src.modelos.autenticacao.autenticacao import TokenAutenticacao
from src.modelos.evento.evento import Evento, Inscrito, TipoVaga
from src.modelos.evento.eventoQuery import eventoQuery
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
        print(modelo)
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
    def listar(query: eventoQuery) -> list[Evento]:
        resultado: list[Evento]

        if query == eventoQuery.PASSADO:
            dbQuery = {"fimEvento": {"$lt": datetime.now()}}
            resultadoBusca = colecaoEventos.find(dbQuery)
        elif query == eventoQuery.PRESENTE:
            dbQuery = {
                "inicioEvento": {"$lt": datetime.now()},
                "fimEvento": {"$gt": datetime.now()},
            }
            resultadoBusca = colecaoEventos.find(dbQuery)
        elif query == eventoQuery.FUTURO:
            dbQuery = {"inicioEvento": {"$gt": datetime.now()}}
            resultadoBusca = colecaoEventos.find(dbQuery)
        else:
            resultadoBusca = colecaoEventos.find()

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
