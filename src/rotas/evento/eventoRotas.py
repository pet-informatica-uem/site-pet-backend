from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Annotated, BinaryIO

from bson.objectid import ObjectId
from fastapi import (
    APIRouter,
    Depends,
    Form,
    UploadFile,
    status,
)
from src.modelos.evento.evento import Evento
from src.rotas.evento.eventoClad import EventoAtualizar, EventoCriar

from src.modelos.usuario.usuario import Usuario
from src.rotas.evento.eventoControlador import EventoControlador
from src.rotas.usuario.usuarioRotas import getPetianoAutenticado, getUsuarioAutenticado

# Especifica o formato das datas para serem convertidos
formatoString = "%d/%m/%Y %H:%M"

roteador = APIRouter(prefix="/eventos", tags=["Eventos"])


#TODO conferir se é interessante retornar o id
@roteador.get(
    "/",
    name="Recuperar todos os eventos",
    description="Retorna todos os eventos cadastrados no banco de dados.",
)
def getEventos() -> list:
    return EventoControlador.getEventos()


#TODO conferir se é interessante retornar o id
@roteador.get(
    "/{id}",
    name="Recuperar evento por ID",
    description="""
        Recupera um evento cadastrado no banco de dados.
        Falha, caso o evento não exista.
    """,
)
def getEvento(id: str) -> Evento:
    evento: Evento = EventoControlador.getEvento(id)

    return evento


@roteador.post(
    "/",
    name=" Cadastrar evento.",
    description="Cadastra um novo evento.",
    status_code=status.HTTP_201_CREATED,
)
def cadastrarEvento(evento: EventoCriar, usuario: Annotated[Usuario, Depends(getPetianoAutenticado)]):
    # Despacha para o controlador
    EventoControlador.cadastrarEvento(evento)


@roteador.patch(
    "/{id}",
    name="Editar evento",
    description="Edita um evento.",
)
def editarEvento(id: str, evento: EventoAtualizar, usuario: Annotated[Usuario, Depends(getPetianoAutenticado)]):
    # Despacha para o controlador
    EventoControlador.editarEvento(id, evento)


@roteador.put(
        "/{id}/imagens",
        name="Atualizar imagens do evento",
        description="Atualiza as imagens do evento.",
)
def atualizarImagensEvento(
    id: str,
    usuario: Annotated[Usuario, Depends(getPetianoAutenticado)],
    arte: UploadFile | None = None,
    cracha: UploadFile | None = None,
):
    # Despacha para o controlador
    EventoControlador.atualizarImagensEvento(id, arte, cracha)


@roteador.delete(
    "/{id}",
    name="Deletar evento",
    description="Deleta um evento.",
)
def deletarEvento(
    id: str,
    usuario: Annotated[Usuario, Depends(getPetianoAutenticado)],
):
    # Despacha para o controlador
    EventoControlador.deletarEvento(id)



# TODO conferir
@roteador.get(
    "/recuperarInscritos",
    name="Recuperar os inscritos de um determinado evento por ID",
    description="""
        Recupera os dados dos inscritos de um determinado evento, como pagamento, nome, email..
        Falha, caso o evento não exista o evento.
    """,
)
def getInscritosEvento(
    id: str, usuario: Annotated[UsuarioSenha, Depends(getPetianoAutenticado)]
) -> list[dict]:
    inscritosController = EnscritosEventoControlador()

    inscritos: list[dict] = inscritosController.getInscritosEvento(id)

    return inscritos


@roteador.post(
    "/inscricaoUsuarioEmEvento",
    name="Recebe dados da inscrição e realiza a inscrição no evento.",
    description="Recebe o id do inscrito, o id do evento, o nivel do conhecimento do inscrito, o tipo de de inscrição e a situação de pagamento da inscricao em eventos do usuario autenticado.",
    status_code=status.HTTP_201_CREATED,
)
def getDadosInscricaoEvento(
    idUsuario: Annotated[Usuario, Depends(getUsuarioAutenticado)],
    id: Annotated[str, Form(max_length=200)],
    tipoDeInscricao: Annotated[str, Form(max_length=200)],
    pagamento: Annotated[bool, Form()],
    nivelConhecimento: Annotated[str | None, Form(max_length=200)] = None,
):
    inscrito: dict = {
        "idUsuario": idUsuario.paraBd()["_id"],
        "id": id,
        "nivelConhecimento": nivelConhecimento,
        "tipoInscricao": tipoDeInscricao,
        "pagamento": pagamento,
    }

    inscritosControlador = EnscritosEventoControlador()
    situacaoInscricao: bool = inscritosControlador.inscricaoEvento(inscrito)

    return situacaoInscricao
