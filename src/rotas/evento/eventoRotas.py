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

    Parâmetros:
        query (IntervaloBusca): Parâmetro de filtro para busca dos eventos.

    Retorno:
        list[Evento]: Lista de objetos Evento que correspondem aos filtros especificados.
    """
    return EventoControlador.getEventos(query)


@roteador.get(
    "/{id}",
    name="Recuperar evento por ID",
    description="""
        Recupera um evento cadastrado no banco de dados.
        Falha, caso o evento não exista.
    """,
)
def getEvento(id: str) -> Evento:
    """
    Recupera um evento específico pelo ID.

    Parâmetros:
        id (str): O identificador único do evento a ser recuperado.

    Retorno:
        Evento: Objeto do tipo Evento correspondente ao ID fornecido.

    Exceções:
        HTTPException: Lançada se o evento com o ID especificado não for encontrado.
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

    Parâmetros:
        evento (EventoCriar): Objeto contendo os dados do evento a ser cadastrado.
        usuario (Usuario): Usuário autenticado responsável pela criação do evento. 
                            Apenas um petiano pode criar um evento.

    Retorno:
        None: A função não retorna nenhum valor, mas cria um novo evento no banco de dados.
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

    Parâmetros:
        id (str): Identificador único do evento a ser editado.
        evento (EventoAtualizar): Dados atualizados do evento.
        usuario (Usuario): Usuário autenticado responsável pela edição.
                            Apenas um petiano pode editar um evento.

    Retorno:
        None: A função não retorna nenhum valor, mas atualiza o evento no banco de dados.
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

    Parâmetros:
        id (str): Identificador do evento.
        usuario (Usuario): Usuário autenticado responsável pela atualização.
                            Apenas um petiano pode atualizar as imagens de um evento.
        arte (UploadFile | None): Arquivo opcional de imagem para arte.
        cracha (UploadFile | None): Arquivo opcional de imagem para crachá.

    Retorno:
        None: A função não retorna nenhum valor, mas atualiza as imagens do evento.
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

    Parâmetros:
        id (str): Identificador do evento a ser deletado.
        usuario (Usuario): Usuário autenticado que solicita a exclusão.
                            Apenas um petiano pode deletar um evento.

    Retorno:
        None: A função não retorna nenhum valor, mas remove o evento do banco de dados.
    """
    # Despacha para o controlador
    EventoControlador.deletarEvento(id)
