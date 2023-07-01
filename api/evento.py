from typing import Annotated
from datetime import datetime

from fastapi import (
    APIRouter,
    Form,
    UploadFile,
    status,
    HTTPException,
    Request,
    Response,
)

from app.models.evento import DadosEvento, DadosEventoOpcional
from app.controllers.evento import controladorNovoEvento

# Especifica o formato das datas para serem convertidos
formatoString = "%d/%m/%Y %H:%M"

roteador = APIRouter(prefix="/evento", tags=["Eventos"])


@roteador.post(
    "/novo",
    name="Novo evento",
    description="Valida as informações e cria um novo evento.",
    status_code=status.HTTP_201_CREATED,
)
def criaEvento(
    response: Response,
    nomeEvento: Annotated[str, Form()],
    resumo: Annotated[str, Form()],
    preRequisitos: Annotated[str, Form()],
    dataEvento: Annotated[str, Form()],
    dataInicioInscr: Annotated[str, Form()],
    dataFimInscr: Annotated[str, Form()],
    local: Annotated[str, Form()],
    vagasComNote: Annotated[int, Form()],
    vagasSemNote: Annotated[int, Form()],
    cargaHoraria: Annotated[int, Form()],
    valor: Annotated[int, Form()],
    imagemArte: UploadFile,
    imagemQrCode: UploadFile | None = None,
    evento: str = None,
):
    dadosEvento = DadosEvento(
        nomeEvento,
        resumo=resumo,
        preRequisitos=preRequisitos,
        dataHoraEvento=datetime.strptime(dataEvento, formatoString),
        inicioInscricao=datetime.strptime(dataInicioInscr, formatoString),
        fimInscricao=datetime.strptime(dataFimInscr, formatoString),
        local=local,
        vagasComNote=vagasComNote,
        vagasSemNote=vagasSemNote,
        cargaHoraria=cargaHoraria,
        valor=valor,
        arteEvento="",
        arteQrcode="",
    )

    imagens = {"arte": imagemArte, "qrcode": imagemQrCode}

    # Passa os dados e as imagens do evento para o controlador
    if not evento:
        retorno = controladorNovoEvento(dadosEvento, imagens)
    else:
        retorno = controladorEditaEvento(evento, dadosEvento, imagens)

    # Trata o retorno do controlador
    sucesso = ["200", "201"]
    if retorno["status"] not in sucesso:
        raise HTTPException(
            status_code=int(retorno["status"]), detail=retorno["mensagem"]
        )
    else:
        response.status_code = retorno["status"]
        return {"mensagem": retorno["mensagem"]}


@roteador.patch(
    "/editar",
    name="Editar evento",
    description="Edita um evento a partir do seu id e algum dado a ser alterado.",
    status_code=status.HTTP_200_OK,
)
def editaEvento(
    evento: str,
    responde: Response,
    nomeEvento: Annotated[str, Form()] = None,
    resumo: Annotated[str, Form()] = None,
    preRequisitos: Annotated[str, Form()] = None,
    dataEvento: Annotated[str, Form()] = None,
    dataInicioInscr: Annotated[str, Form()] = None,
    dataFimInscr: Annotated[str, Form()] = None,
    local: Annotated[str, Form()] = None,
    vagasComNote: Annotated[int, Form()] = None,
    vagasSemNote: Annotated[int, Form()] = None,
    cargaHoraria: Annotated[int, Form()] = None,
    valor: Annotated[int, Form()] = None,
    imagemArte: UploadFile = None,
    imagemQrCode: UploadFile = None,
):
    dadosEvento = DadosEventoOpcional(
        nomeEvento=nomeEvento,
        resumo=resumo,
        preRequisitos=preRequisitos,
        dataEvento=dataEvento,
        dataInicioInscr=dataInicioInscr,
        dataFimInscr=dataFimInscr,
        local=local,
        vagasComNote=vagasComNote,
        vagasSemNote=vagasSemNote,
        cargaHoraria=cargaHoraria,
        valor=valor,
        imagemArte="",
        imagemQrCode="",
    )

    imagens = {"arte": imagemArte, "imagemQrCode": imagemQrCode}

    # Verifica se são todos nulos
    if all(x is None for x in dict(dadosEvento.values()) for x in imagens.values()):
        responde.status_code = status.HTTP_204_NO_CONTENT
        return {"mensagem": "Sem conteúdo."}

    # Despacha para o controlador
    payload = {
        "evento": evento,
        "dadosEventoNew": dadosEvento,
        "imagensNew": imagens,
    }
    retorno = editaEventoControlador(payload)
