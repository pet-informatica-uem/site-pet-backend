from typing import Annotated

from fastapi import APIRouter, Depends, UploadFile, status

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
    description="""Cadastra um novo inscrito. 
                   tipoVaga = true para vaga com note.
                   tipoVaga = false para vaga sem note.
                   nivelConhecimento 1-5""",
    status_code=status.HTTP_201_CREATED,
)
def cadastrarInscrito(
    idEvento: str,
    inscrito: InscritoCriar,
    # TODO comprovante: UploadFile,
    usuario: Annotated[Usuario, Depends(getUsuarioAutenticado)],
):
    # Despacha para o controlador
    InscritosControlador.cadastrarInscrito(idEvento, usuario.id, inscrito)


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
    if usuario.id == id or usuario.tipoConta == TipoConta.PETIANO:
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
    if usuario.id == id or usuario.tipoConta == TipoConta.PETIANO:
        inscrito: InscritoDeletar = InscritoDeletar(
            idEvento=idEvento, idUsuario=idInscrito
        )
        InscritosControlador.removerInscrito(inscrito)
    else:
        raise NaoAutorizadoExcecao()