from typing import Annotated
from datetime import datetime

from fastapi import APIRouter, Form, UploadFile, status, HTTPException

from app.controllers.evento import controladorNovoEvento


# Especifica o formato das datas para serem convertidos
formatoString = "%d/%m/%Y"

roteador = APIRouter(prefix="/evento", tags=["Eventos"])


@roteador.post(
    "/novo",
    name="Novo evento",
    description="Valida as informações e cria um novo evento.",
    status_code=status.HTTP_201_CREATED,
)
def criaEvento(
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
    imagemQrCode: UploadFile | None,
):
    dadosEvento = {
        "nome evento": nomeEvento,
        "resumo": resumo,
        "pré-requisitos": preRequisitos,
        "data/hora evento": datetime.strptime(dataEvento, formatoString),
        "data inicio inscrição": datetime.strptime(dataInicioInscr, formatoString),
        "data fim inscrição": datetime.strptime(dataFimInscr, formatoString),
        "local": local,
        "vagas ofertadas": {
            "vagas com notebook": vagasComNote,
            "vagas sem notebook": vagasSemNote,
        },
        "carga horária": cargaHoraria,
        "valor": valor,
    }

    imagens = {"arte": imagemArte, "qrcode": imagemQrCode}

    # Passa os dados e as imagens do evento para o controlador
    retorno = controladorNovoEvento(dadosEvento, imagens)

    # Trata o retorno do controlador
    if retorno != "201":
        raise HTTPException(
            status_code=int(retorno.get("status")), detail=retorno.get("mensagem")
        )
    else:
        return {"mensagem": retorno.get("mensagem")}
