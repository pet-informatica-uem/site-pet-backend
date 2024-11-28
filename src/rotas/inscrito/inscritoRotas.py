from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, File, UploadFile, status

from src.modelos.excecao import NaoAutorizadoExcecao
from src.modelos.inscrito.inscritoClad import (
    InscritoAtualizar,
    InscritoCriar,
    InscritoDeletar,
    InscritoLer,
)
from src.modelos.usuario.usuario import TipoConta, Usuario
from src.rotas.inscrito.inscritoControlador import InscritosControlador
from src.rotas.usuario.usuarioRotas import getPetianoAutenticado, getUsuarioAutenticado

roteador = APIRouter(prefix="/eventos", tags=["Eventos"])


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
    """
    Cadastra um inscrito em um evento.

    :param tasks: Gerenciador de tarefas
    :param usuario: Usuário autenticado que está realizando a inscrição.
    :param idEvento: Identificador único do evento.
    :param inscrito: Dados de um inscrito.
    :param comprovante: Arquivo de comprovante de pagamento.
    """
    # Despacha para o controlador
    InscritosControlador.cadastrarInscrito(
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
    return InscritosControlador.getInscritos(idEvento)


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
    
    :raises NaoAutorizadoExcecao: Se o usuário não tiver permissão para editar os dados do inscrito.
    """
    # Verifica se o usuário corresponde ao inscrito ou se é um petiano autorizado.
    if usuario.id == id or usuario.tipoConta == TipoConta.PETIANO:
        # Despacha para o controlador
        InscritosControlador.editarInscrito(idEvento, idInscrito, inscrito)
    else:
        raise NaoAutorizadoExcecao()


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
    # Verifica se o usuário corresponde ao inscrito ou se é um petiano autorizado.
    if usuario.id == id or usuario.tipoConta == TipoConta.PETIANO:
        inscrito: InscritoDeletar = InscritoDeletar(
            idEvento=idEvento, idUsuario=idInscrito
        )
        # Despacha para o controlador
        InscritosControlador.removerInscrito(inscrito)
    else:
        raise NaoAutorizadoExcecao()
