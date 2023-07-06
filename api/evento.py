from dataclasses import asdict, dataclass
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    Form,
    HTTPException,
    Response,
    UploadFile,
    status,
)

from api.usuario import tokenAcesso
from app.controllers.evento import (
    EventoController,
    controladorEditarEvento,
    controladorNovoEvento,
)
from app.controllers.inscritosEvento import InscritosEventoController
from app.controllers.usuario import getUsuarioAutenticadoControlador
from app.model.evento import DadosEvento
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


roteador = APIRouter(prefix="/eventos", tags=["Eventos"])


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
            status_code=eventos.get("status"), detail=eventos.get("mensagem")
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
            status_code=inscritos.get("status"), detail=inscritos.get("mensagem")
        )

    return {"mensagem": inscritos.get("mensagem")}
