from typing import Annotated
from typing import Optional

from fastapi import APIRouter, Depends, UploadFile, status, BackgroundTasks, Form, File
from src.modelos.evento.evento import NivelConhecimento, TipoVaga
from src.modelos.evento.evento import Evento
from src.modelos.evento.eventoClad import (
    EventoAtualizar,
    EventoCriar,
    EventoLer,
    InscritoAtualizar,
    InscritoCriar,
    InscritoLer,
)
from src.modelos.evento.intervaloBusca import IntervaloBusca
from src.modelos.usuario.usuario import Usuario
from src.rotas.evento.eventoControlador import EventoControlador
from src.rotas.usuario.usuarioRotas import getPetianoAutenticado, getUsuarioAutenticado

roteador = APIRouter(prefix="/eventos", tags=["Eventos"])


@roteador.get(
    "/",
    name="Recuperar eventos",
    description="Retorna todos os eventos cadastrados no banco de dados filtrados pelo parâmetro 'query'.",
)
def getEventos(query: Optional[IntervaloBusca] = None) -> list[Evento]:
    """
    Retorna todos os eventos cadastrados no banco de dados, aplicando filtros conforme o parâmetro 'query'.

    :param query (IntervaloBusca): Parâmetro de filtro para busca dos eventos.

    :return list[Evento]: Lista de objetos Evento que correspondem aos filtros especificados.
    """
    return EventoControlador.getEventos(query)


@roteador.get(
    "/{id}",
    name="Recuperar evento por ID",
    description="""
        Recupera um evento cadastrado no banco de dados pelo seu id.
        Falha, caso o evento não exista.
    """,
    response_model=EventoLer,
)
def getEvento(id: str) -> Evento:
    """
    Recupera um evento específico pelo ID.

    :param id (str): O identificador único do evento a ser recuperado.

    :return Evento: Objeto do tipo Evento correspondente ao ID fornecido.

    :raises HTTPException: Lançada se o evento com o ID especificado não for encontrado.
    """
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
    """
    Cadastra um novo evento no sistema.

    :param evento: Objeto contendo os dados do evento a ser cadastrado.
    :param usuario: Usuário autenticado responsável pela criação do evento.
                    Apenas um petiano pode criar um evento.
    """
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
    """
    Edita um evento existente.

    :param id: Identificador único do evento a ser editado.
    :param evento: Dados atualizados do evento.
    :param usuario: Usuário autenticado responsável pela edição.
                    Apenas um petiano pode editar um evento.
    """
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
    """
    Atualiza as imagens de arte e crachá associadas a um evento.

    :param id: Identificador do evento.
    :param usuario: Usuário autenticado responsável pela atualização.
                    Apenas um petiano pode atualizar as imagens de um evento.
    :param arte: Arquivo opcional de imagem para arte.
    :param cracha: Arquivo opcional de imagem para crachá.
    """
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
    """
    Exclui um evento específico do banco de dados.

    :param id: Identificador do evento a ser deletado.
    :param usuario: Usuário autenticado que solicita a exclusão.
                    Apenas um petiano pode deletar um evento.
    """
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
    tipoVaga: TipoVaga = Form(...),
    nivelConhecimento: NivelConhecimento = Form(...),
    comprovante: UploadFile | None = File(None),
):
    inscrito = InscritoCriar(
        tipoVaga=tipoVaga,
        nivelConhecimento=nivelConhecimento,
    )

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
    """
    Recupera todos os inscritos de um evento.

    :param idEvento: Identificador único do evento.
    :param usuario: Usuário autenticado como petiano.
    """
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
    """
    Edita os dados de um inscrito em um evento.

    :param idEvento: Identificador único do evento.
    :param idInscrito: Identificador único do inscrito a ser editado.
    :param inscrito: Dados atualizados do inscrito.
    :param usuario: Usuário autenticado que solicita a edição.
    """
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
    """
    Deleta um inscrito de um evento.

    :param idEvento: Identificador único do evento.
    :param idInscrito: Identificador único do inscrito a ser deletado.
    :param usuario: Usuário autenticado que solicita a exclusão.

    :raises NaoAutorizadoExcecao: Se o usuário não tiver permissão para deletar o inscrito do evento.
    """
    return EventoControlador.removerInscrito(idEvento, idInscrito)
