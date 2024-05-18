from typing import Annotated
from fastapi import APIRouter, Depends
from src.modelos.excecao import NaoAutorizadoExcecao
from src.modelos.usuario.usuario import TipoConta, Usuario
from src.rotas.img.imgControlador import ImagemControlador
from src.rotas.usuario.usuarioRotas import getUsuarioAutenticado

roteador = APIRouter(prefix="/img", tags=["Imagens"])
@roteador.get(
    "/usuarios/{id}/foto",
    name="Recuperar imagem por ID",
    description="Recupera a imagem de um usuário por ID",
)
def getImagemUsuario(id: str):
    return ImagemControlador.getImagemUsuario(id)

@roteador.get(
    "/eventos/{id}/arte",
    name="Recuperar imagem por ID",
    description="Recupera a arte (capa) de um evento por ID",
)
def getImagemEvento(id: str):
    return ImagemControlador.getImagemEvento(id)

@roteador.get(
    "/eventos/{id}/cracha",
    name="Recuperar template do crachá do evento",
    description="Recupera o template do crachá do evento com o ID `id`",
)
def getCrachaEvento(id: str):
    return ImagemControlador.getCrachaEvento(id)

@roteador.get(
    "/eventos/{idEvento}/inscritos/{idInscrito}/comprovante",
    name="Recuperar comprovante de inscrição",
    description="Recupera o comprovante de inscrição de um inscrito em um evento. O comprovante deve ser do próprio usuário, ou o usuário deve ser petiano.",
)
def getComprovanteInscrito(
    usuario: Annotated[Usuario, Depends(getUsuarioAutenticado)],
    idEvento: str,
    idInscrito: str
):
    if usuario.tipoConta == TipoConta.PETIANO or usuario.id == idInscrito:
        return ImagemControlador.getComprovanteInscrito(idEvento, idInscrito)
    else:
        raise NaoAutorizadoExcecao()