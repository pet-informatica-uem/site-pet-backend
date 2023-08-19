import logging
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from src.rotas.petiano.petianoClad import Petiano
from src.modelos.excecao import (
    APIExcecaoBase,
    NaoEncontradoExcecao,
    UsuarioJaExisteExcecao,
)
from src.modelos.usuario.usuario import TipoConta, Usuario


from src.config import config

cliente: MongoClient = MongoClient(str(config.URI_BD))

colecaoTokens = cliente[config.NOME_BD]["authTokens"]

colecaoUsuarios = cliente[config.NOME_BD]["usuarios"]
colecaoUsuarios.create_index("email", unique=True)
colecaoUsuarios.create_index("cpf", unique=True)

colecaoEventos = cliente[config.NOME_BD]["eventos"]
colecaoInscritos = cliente[config.NOME_BD]["inscritos"]


# operações banco de dados
def buscar(colecao: type[Usuario], indice: str, chave: str) -> Usuario:
    if colecao is Usuario:
        # Verifica se o usuário está cadastrado no bd
        if not colecaoUsuarios.find_one({indice: chave}):
            raise NaoEncontradoExcecao(mensagem="O Usuário não foi encontrado.")
        else:
            return Usuario(**colecaoUsuarios.find_one({indice: chave}))  # type: ignore
    # elif type(colecao) is Evento:
    #     # Verifica se o evento está cadastrado no bd
    #     if not colecaoEventos.find_one({incice: chave}):
    #         raise NaoEncontradoExcecao(mensagem="O evento não foi encontrado.")
    #     else:
    #         return Evento = Evento(**colecaoEventos.find_one({incice: chave})) # type: ignore
    else:
        raise NaoEncontradoExcecao(mensagem="A coleção não foi encontrada.")


def criar(modelo: Usuario):
    if type(modelo) is Usuario:
        # cria usuario no bd
        try:
            colecaoUsuarios.insert_one(modelo.model_dump(by_alias=True))
        except DuplicateKeyError:
            logging.error("Usuário já existe no banco de dados")
            raise UsuarioJaExisteExcecao()
    raise APIExcecaoBase(mensagem="Modelo Inválido.")


def atualizar(modelo: Usuario):
    if type(modelo) is Usuario:
        colecaoUsuarios.update_one({"_id": modelo.id}, modelo.model_dump(by_alias=True))


def deletar(colecao: type[Usuario], id: str):
    if colecao is Usuario:
        colecaoUsuarios.delete_one({"_id": id})


def listar(colecao: type[Usuario] | type[Petiano]) -> list[Usuario] | list[Petiano]:
    if colecao is Usuario:
        return [Usuario(**u) for u in colecaoUsuarios.find()]
    if colecao is Petiano:
        return [
            Usuario(**u) for u in colecaoUsuarios.find({"tipoConta": TipoConta.PETIANO})
        ]

    raise NaoEncontradoExcecao(mensagem="Coleção não encontrada")
