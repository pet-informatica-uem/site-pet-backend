from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile, status, BackgroundTasks
from src.modelos.evento.evento import Evento
from src.modelos.evento.eventoClad import (
    EventoAtualizar,
    EventoCriar,
    EventoLer,
    InscritoAtualizar,
    InscritoCriar,
    InscritoLer,
)
from src.modelos.evento.eventoQuery import eventoQuery
from src.modelos.usuario.usuario import Usuario, TipoConta
from src.rotas.evento.eventoControlador import EventoControlador
from src.rotas.usuario.usuarioRotas import getPetianoAutenticado, getUsuarioAutenticado

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
    return evento.model_dump(by_alias=True)  # type: ignore

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


##########################################################INSCRITOS
@roteador.post(
    "/{idEvento}/inscritos",
    name="Cadastrar inscrito",
    description="Cadastra um novo inscrito.\n\n "
    "- tipoVaga = comNotebook para vaga com note.\n\n"
    "- tipoVaga = semNotebook para vaga sem note.\n\n"
    "- nivelConhecimento 1-5",
    status_code=status.HTTP_201_CREATED,
)
def cadastrarInscrito(
    tasks: BackgroundTasks,
    usuario: Annotated[Usuario, Depends(getUsuarioAutenticado)],
    idEvento: str,
    inscrito: InscritoCriar = Depends(),
    comprovante: UploadFile | None = None,
):
    # Despacha para o controlador
    EventoControlador.cadastrarInscrito(    
        idEvento, usuario.id, inscrito, comprovante, tasks
    )

@roteador.get(
    "/{idEvento}/inscritos",
    name="Recuperar inscritos",
    description="Recupera os inscritos de um evento.",
    response_model=list[InscritoLer],
)
def getInscritos(
    idEvento: str, usuario: Annotated[Usuario, Depends(getPetianoAutenticado)]
):
    # Despacha para o controlador
    return EventoControlador.getInscritos(idEvento)

@roteador.patch(
    "/{idEvento}/inscritos/{idInscrito}",
    name="Editar inscrito",
    description="Edita um inscrito.",
)
def editarInscrito(
    idEvento: str,
    idInscrito: str,
    inscrito: InscritoAtualizar,
    usuario: Annotated[Usuario, Depends(getUsuarioAutenticado)],
):
    return EventoControlador.editarInscrito(idEvento, idInscrito, inscrito)

@roteador.delete(
    "/{idEvento}/inscritos/{idInscrito}",
    name="Remover inscrito",
    description="Remove um inscrito.",
)
def removerInscrito(
    idEvento: str,
    idInscrito: str,
    usuario: Annotated[Usuario, Depends(getUsuarioAutenticado)],
):
        
    return EventoControlador.removerInscrito(idEvento, idInscrito)
