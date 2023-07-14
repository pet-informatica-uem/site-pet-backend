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

from src.modelos.autenticacao.autenticacaoTokenBD import AuthTokenBD
from src.modelos.evento.evento import DadosEvento
from src.modelos.usuario.usuario import UsuarioSenha
from src.rotas.evento.eventoControlador import (
    EventoController,
    controladorDeletaEvento,
    controladorEditarEvento,
    controladorNovoEvento,
    inscricaoEventoControlador,
)
from src.rotas.evento.eventoInscritosControlador import InscritosEventoController
from src.rotas.usuario.usuarioRotas import getPetianoAutenticado,tokenAcesso

# Especifica o formato das datas para serem convertidos
formatoString = "%d/%m/%Y %H:%M"

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


@roteador.post(
    "/cadastroEmEvento",
    name="Recebe dados da inscrição e realiza a inscrição no evento.",
    description="Recebe o id do inscrito, o id do evento, o nivel do conhecimento do inscrito, o tipo de de inscrição e a situação de pagamento da inscricao em eventos do usuario autenticado.",
    status_code=status.HTTP_201_CREATED,
)
def getDadosInscricaoEvento(
    token: Annotated[str, Depends(tokenAcesso)],
    idEvento: Annotated[str, Form(max_length=200)],
    tipoDeInscricao: Annotated[str, Form(max_length=200)],
    pagamento: Annotated[bool, Form()],
    nivelConhecimento: Annotated[str | None, Form(max_length=200)] = None,
):
    conexaoAuthToken = AuthTokenBD()

    resp: dict = conexaoAuthToken.getIdUsuarioDoToken(token)
    idUsuario: str = resp["mensagem"]

    resposta: dict = inscricaoEventoControlador(
        idUsuario, idEvento, nivelConhecimento, tipoDeInscricao, pagamento
    )

    statusResposta: str = resposta["status"]
    mensagemResposta: str = resposta["mensagem"]
    if statusResposta == "400":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=mensagemResposta
        )
    if statusResposta == "404":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=mensagemResposta
        )
    if statusResposta == "409":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=mensagemResposta
        )
    if statusResposta == "406":
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=mensagemResposta
        )
    if statusResposta == "410":
        raise HTTPException(status_code=status.HTTP_410_GONE, detail=mensagemResposta)

    resposta["status"] = "201"
    resposta["mensagem"] = "Usuario inscrito com sucesso!"
    return resposta
