from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile, status

from src.modelos.evento.evento import Evento
from src.modelos.evento.eventoClad import EventoAtualizar, EventoCriar, EventoLer
from src.modelos.evento.intervaloBusca import IntervaloBusca
from src.modelos.usuario.usuario import Usuario
from src.rotas.evento.eventoControlador import EventoControlador
from src.rotas.usuario.usuarioRotas import getPetianoAutenticado, getUsuarioAutenticado

# Especifica o formato das datas para serem convertidos
formatoString = "%d/%m/%Y %H:%M"

roteador = APIRouter(prefix="/eventos", tags=["Eventos"])


@roteador.get(
    "/",
    name="Recuperar eventos",
    description="Retorna todos os eventos cadastrados no banco de dados filtrados pelo parâmetro 'query'.",
)
def getEventos(query: IntervaloBusca) -> list[Evento]:
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
)
def getEvento(id: str) -> Evento:
    """
    Recupera um evento específico pelo ID.

    :param id (str): O identificador único do evento a ser recuperado.

    :return Evento: Objeto do tipo Evento correspondente ao ID fornecido.

    :raises HTTPException: Lançada se o evento com o ID especificado não for encontrado.
    """
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
