from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile, status

from src.modelos.evento.evento import Evento
from src.modelos.evento.eventoClad import EventoAtualizar, EventoCriar, EventoLer
from src.modelos.usuario.usuario import Usuario
from src.rotas.evento.eventoControlador import EventoControlador
from src.rotas.usuario.usuarioRotas import getPetianoAutenticado, getUsuarioAutenticado

from src.modelos.evento.eventoQuery import eventoQuery

# Especifica o formato das datas para serem convertidos
formatoString = "%d/%m/%Y %H:%M"

roteador = APIRouter(prefix="/eventos", tags=["Eventos"])


@roteador.get(
    "/",
    name="Recuperar eventos",
    description="Retorna todos os eventos cadastrados no banco de dados filtrados pelo parâmetro 'query'.",
)
def getEventos(query: eventoQuery) -> list[Evento]:
    return EventoControlador.getEventos(query)


@roteador.get(
    "/{id}",
    name="Recuperar evento por ID",
    description="""
        Recupera um evento cadastrado no banco de dados.
        Falha, caso o evento não exista.
    """,
    response_model=EventoLer,
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
def cadastrarEvento(
    evento: EventoCriar, usuario: Annotated[Usuario, Depends(getPetianoAutenticado)]
):
    # Despacha para o controlador
    EventoControlador.cadastrarEvento(evento)


@roteador.patch(
    "/{id}",
    name="Editar evento",
    description="Edita um evento.",
)
def editarEvento(
    id: str,
    evento: EventoAtualizar,
    usuario: Annotated[Usuario, Depends(getPetianoAutenticado)],
):
    # Despacha para o controlador
    EventoControlador.editarEvento(id, evento)


# TODO tem que ser opcional
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
