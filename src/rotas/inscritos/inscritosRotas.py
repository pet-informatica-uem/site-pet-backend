from typing import Annotated
from fastapi import APIRouter, Depends
from modelos.excecao import NaoAutorizadoExcecao
from rotas.inscritos.inscritosControlador import InscritosControlador
from src.modelos.usuario.usuario import TipoConta, Usuario
from src.rotas.usuario.usuarioRotas import getPetianoAutenticado, getUsuarioAutenticado

from src.modelos.inscritos.inscrito import Inscrito, InscritoCriar


roteador = APIRouter(prefix="/eventos", tags=["Eventos"])

@roteador.post(
    "/{idEvento}/inscritos",
    name="Cadastrar inscrito",
    description="Cadastra um novo inscrito.",
)
def cadastrarInscrito(idEvento: str, inscrito: InscritoCriar, usuario: Annotated[Usuario, Depends(getUsuarioAutenticado)]):
    # Despacha para o controlador
    InscritosControlador.cadastrarInscrito(idEvento, usuario.id, inscrito)


@roteador.delete(
    "/{idEvento}/inscritos/{idInscrito}",
    name="Remover inscrito",
    description="Remove um inscrito.",
)
def removerInscrito(idEvento: str, idInscrito: str, usuario: Annotated[Usuario, Depends(getUsuarioAutenticado)]):
    if usuario.id == id or usuario.tipoConta == TipoConta.PETIANO:
        InscritosControlador.removerInscrito(idEvento, idInscrito)
    else:
        raise NaoAutorizadoExcecao()
    


@roteador.get(
    "/{idEvento}/inscritos",
    name="Recuperar inscritos",
    description="Recupera os inscritos de um evento.",
)
def getInscritos(idEvento: str, usuario: Annotated[Usuario, Depends(getPetianoAutenticado)]):
    # Despacha para o controlador
    return InscritosControlador.getInscritos(idEvento)


@roteador.patch(
    "/{idEvento}/inscritos/{idInscrito}",
    name="Editar inscrito",
    description="Edita um inscrito.",
)
def editarInscrito(idEvento: str, idInscrito: str, inscrito: InscritoCriar, usuario: Annotated[Usuario, Depends(getUsuarioAutenticado)]):
    if usuario.id == id or usuario.tipoConta == TipoConta.PETIANO:
        InscritosControlador.editarInscrito(idEvento, idInscrito, inscrito)
    else:
        raise NaoAutorizadoExcecao()

