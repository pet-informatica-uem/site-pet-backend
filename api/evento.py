from dataclasses import dataclass, asdict
from typing import Annotated

from fastapi import (
    APIRouter,
    Form,
    UploadFile,
    status,
    HTTPException,
    Response,
    Depends,
)

from api.usuario import tokenAcesso
from app.model.evento import DadosEvento
from app.controllers.usuario import getUsuarioAutenticadoControlador
from app.controllers.evento import controladorNovoEvento, controladorEditarEvento
from core.usuario import ehPetiano

# Especifica o formato das datas para serem convertidos
formatoString = "%d/%m/%Y %H:%M"

roteador = APIRouter(prefix="/evento", tags=["Eventos"])


# Classe de dados para receber o formulário com as informações do evento
@dataclass
class FormEvento:
    nomeEvento: str = Form(...)
    resumo: str = Form(...)
    preRequisitos: str = Form(...)
    dataHoraEvento: str = Form(...)
    inicioInscricao: str = Form(...)
    fimInscricao: str = Form(...)
    local: str = Form(...)
    vagasComNote: int = Form(...)
    vagasSemNote: int = Form(...)
    cargaHoraria: int = Form(...)
    valor: int = Form(...)


@roteador.post(
    "/novo",
    name="Novo evento",
    description="Valida as informações e cria um novo evento.",
    status_code=status.HTTP_201_CREATED,
)
def criaEvento(
    response: Response,
    token: Annotated[str, Depends(tokenAcesso)],
    arteEvento: UploadFile,
    arteQrcode: UploadFile = None,
    formEvento: FormEvento = Depends(),
):
    # Cria um dicionário para as imagens
    imagens = {"arteEvento": arteEvento.file, "arteQrcode": None}
    if arteQrcode:
        imagens.update(arteQrcode=arteQrcode.file)

    # Recupera o ID do usuário
    dados = getUsuarioAutenticadoControlador(token)
    idUsuario = dict(dados["mensagem"])["id"]

    # Verifica se o usuario é petiano
    retorno = ehPetiano(idUsuario)
    if retorno["status"] != "200":
        raise HTTPException(
            status_code=int(retorno["status"]), detail=retorno["mensagem"]
        )

    # Passa os dados e as imagens do evento para o controlador
    dadosEvento = DadosEvento(**asdict(formEvento))
    retorno = controladorNovoEvento(dadosEvento, imagens)

    # Trata o retorno do controlador
    if retorno["status"] != "201":
        raise HTTPException(
            status_code=int(retorno["status"]), detail=retorno["mensagem"]
        )
    else:
        response.status_code = int(retorno["status"])
        return {"mensagem": retorno["mensagem"]}


@roteador.post(
    "/editar/{nomeEventoOld}",
    name="Editar evento",
    description="Valida as informações e edita um evento.",
    status_code=status.HTTP_200_OK,
)
def editaEvento(
    nomeEventoOld: str,
    response: Response,
    token: Annotated[str, Depends(tokenAcesso)],
    formEvento: FormEvento = Depends(),
    arteEvento: UploadFile = None,
    arteQrcode: UploadFile = None,
):
    # Cria um dicionário para as imagens
    imagens = {"arteEvento": None, "arteQrcode": None}
    if arteEvento:
        imagens.update(arteEvento=arteEvento.file)
    if arteQrcode:
        imagens.update(arteQrcode=arteQrcode.file)

    # Recupera o ID do usuário
    dados = getUsuarioAutenticadoControlador(token)
    idUsuario = dict(dados["mensagem"])["id"]

    # Verifica se o usuario é petiano
    retorno = ehPetiano(idUsuario)
    if retorno["status"] != "200":
        raise HTTPException(
            status_code=int(retorno["status"]), detail=retorno["mensagem"]
        )

    # Passa os dados e as imagens do evento para o controlador
    dadosEvento = DadosEvento(**asdict(formEvento))
    retorno = controladorEditarEvento(nomeEventoOld, dadosEvento, imagens)

    # Trata o retorno do controlador
    if retorno["status"] != "200":
        raise HTTPException(
            status_code=int(retorno["status"]), detail=retorno["mensagem"]
        )
    else:
        response.status_code = int(retorno["status"])
        return {"mensagem": retorno["mensagem"]}
