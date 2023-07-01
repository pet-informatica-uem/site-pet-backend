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

from app.model.evento import DadosEvento 
from app.controllers.evento import controladorNovoEvento, controladorEditarEvento

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
        nomeEvento=nomeEvento,
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
        retorno = controladorEditarEvento(evento, dadosEvento, imagens)

    # Trata o retorno do controlador
    sucesso = ["200", "201"]
    if retorno["status"] not in sucesso:
        raise HTTPException(
            status_code=int(retorno["status"]), detail=retorno["mensagem"]
        )
    else:
        response.status_code = int(retorno["status"])
        return {"mensagem": retorno["mensagem"]}
