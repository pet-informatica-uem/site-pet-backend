from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Annotated, BinaryIO

from fastapi import (
    APIRouter,
    Depends,
    Form,
    HTTPException,
    Response,
    UploadFile,
    status,
)

from api.usuario import getPetianoAutenticado
from app.controllers.evento import (
    EventoController,
    controladorEditarEvento,
    controladorNovoEvento,
    controladorDeletaEvento,
)
from app.controllers.inscritosEvento import InscritosEventoController
from app.model.evento import DadosEvento
from app.model.usuario import UsuarioSenha

roteador = APIRouter(prefix="/evento", tags=["Eventos"])


# Classe de dados para receber o formulário com as informações do evento
@dataclass
class FormEvento:
    nomeEvento: str = Form(...)
    resumo: str = Form(...)
    preRequisitos: str = Form(...)
    dataHoraEvento: datetime = Form(...)
    inicioInscricao: datetime = Form(...)
    fimInscricao: datetime = Form(...)
    local: str = Form(...)
    vagasComNote: int = Form(...)
    vagasSemNote: int = Form(...)
    cargaHoraria: int = Form(...)
    valor: float = Form(...)


@roteador.post(
    "/novo",
    name="Novo evento",
    description="Valida as informações e cria um novo evento.",
    status_code=status.HTTP_201_CREATED,
)
def criaEvento(
    response: Response,
    usuario: Annotated[UsuarioSenha, Depends(getPetianoAutenticado)],
    arteEvento: UploadFile,
    arteQrcode: UploadFile | None = None,
    formEvento: FormEvento = Depends(),
):
    # Cria um dicionário para as imagens
    imagens: dict[str, BinaryIO | None] = {
        "arteEvento": arteEvento.file,
        "arteQrcode": None,
    }
    if arteQrcode:
        imagens["arteQrcode"] = arteQrcode.file

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
        return {retorno["mensagem"]}


@roteador.post(
    "/editar/{idEvento}",
    name="Editar evento",
    description="Valida as informações e edita um evento.",
    status_code=status.HTTP_200_OK,
)
def editaEvento(
    idEvento: str,
    response: Response,
    usuario: Annotated[UsuarioSenha, Depends(getPetianoAutenticado)],
    formEvento: FormEvento = Depends(),
    arteEvento: UploadFile | None = None,
    arteQrcode: UploadFile | None = None,
):
    # Cria um dicionário para as imagens
    imagens: dict[str, BinaryIO | None] = {"arteEvento": None, "arteQrcode": None}
    if arteEvento:
        imagens["arteEvento"] = arteEvento.file
    if arteQrcode:
        imagens["arteQrcode"] = arteQrcode.file

    # Passa os dados e as imagens do evento para o controlador
    dadosEvento = DadosEvento(**asdict(formEvento))
    retorno = controladorEditarEvento(idEvento, dadosEvento, imagens)

    # Trata o retorno do controlador
    if retorno["status"] != "200":
        raise HTTPException(
            status_code=int(retorno["status"]), detail=retorno["mensagem"]
        )
    else:
        response.status_code = int(retorno["status"])
        return {retorno["mensagem"]}


@roteador.delete(
    "/deletar/{idEvento}",
    name="Deletar evento",
    description="Um usuário petiano pode deletar um evento.",
    status_code=status.HTTP_200_OK,
)
def deletaEvento(
    idEvento: str,
    usuario: Annotated[UsuarioSenha, Depends(getPetianoAutenticado)],
):
    # Despacha para o controlador
    retorno: dict = controladorDeletaEvento(idEvento)

    # Trata o retorno
    if retorno["status"] != "200":
        raise HTTPException(
            status_code=int(retorno["status"]), detail=retorno["mensagem"]
        )
    return retorno


@roteador.get(
    "/listarTodosEventos",
    name="Recuperar todos os eventos",
    description="""
        Recupera todos os eventos cadastrados no banco de dados.
    """,
)
def listarEventos() -> dict:
    eventoController = EventoController()

    eventos = eventoController.listarEventos()
    if eventos.get("status") != "200":
        raise HTTPException(
            status_code=int(eventos["status"]), detail=eventos["mensagem"]
        )

    return {"mensagem": eventos.get("mensagem")}


@roteador.get(
    "/recuperarInscritos",
    name="Recuperar os inscritos de um determinado evento por ID",
    description="""
        Recupera os dados dos inscritos de um determinado evento, como pagamento, nome, email..
        Falha, caso o evento não exista o evento.
    """,
)
def getInscritosEvento(idEvento: str) -> dict:
    inscritosController = InscritosEventoController()

    inscritos = inscritosController.getInscritosEvento(idEvento)
    if inscritos.get("status") != "200":
        raise HTTPException(
            status_code=int(inscritos["status"]), detail=inscritos["mensagem"]
        )

    return {"mensagem": inscritos.get("mensagem")}
