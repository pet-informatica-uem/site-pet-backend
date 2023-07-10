from fastapi import APIRouter, HTTPException
from app.controllers.inscritosEvento import InscritosEventoController
from app.controllers.evento import EventoController
from typing import Annotated

from app.controllers.evento import inscricaoEventoControlador
from fastapi import APIRouter, Depends, Form, HTTPException, status
from api.usuario import tokenAcesso

from app.controllers.usuario import getUsuarioAutenticadoControlador
from app.model.authTokenBD import AuthTokenBD

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

    resp : dict = conexaoAuthToken.getIdUsuarioDoToken(token)
    idUsuario : str = resp["mensagem"]

    resposta : dict = inscricaoEventoControlador(
        idUsuario, idEvento, nivelConhecimento, tipoDeInscricao, pagamento
    )

    statusResposta : str = resposta["status"]
    mensagemResposta : str = resposta["mensagem"]
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
        raise HTTPException(
            status_code=status.HTTP_410_GONE, detail=mensagemResposta
        )

    resposta["status"] = "201"
    resposta["mensagem"] = "Usuario inscrito com sucesso!"
    return resposta
