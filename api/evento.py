from typing import Annotated
from datetime import datetime

from fastapi import APIRouter, Form, UploadFile, status


# Especifica o formato das datas para serem convertidos
formatoString = "%d/%m/%Y"


roteador = APIRouter(prefix="/evento", tags=["Eventos"])


@roteador.post(
    "/novo",
    name="Novo evento",
    description="Valida as informações e cria um novo evento.",
    status_code=status.HTTP_201_CREATED
)
def criaEvento(
    nomeEvento: Annotated[str, Form()],
    resumo: Annotated[str, Form()],
    preRequisitos: Annotated[str, Form()],
    nivelConhecimento: Annotated[str, Form()],
    dataEvento: Annotated[str, Form()],
    dataInicioInscr: Annotated[str, Form()],
    dataFimInscr: Annotated[str, Form()],
    local: Annotated[str, Form()],
    vagasComNote: Annotated[int, Form()],
    vagasSemNote: Annotated[int, Form()],
    cargaHoraria: Annotated[int, Form()],
    valor: Annotated[int, Form()],
    imagemEvento: UploadFile,
    imagemQrCode: UploadFile | None,
):
    dadosEvento = {
        "nome evento": nomeEvento,
        "resumo": resumo,
        "pré-requisitos": preRequisitos,
        "nível conhecimento": nivelConhecimento,
        "data criação": datetime.now(),
        "data/hora evento": datetime.strptime(dataEvento, formatoString),
        "data inicio inscrição": datetime.strptime(dataInicioInscr, formatoString),
        "data fim inscrição": datetime.strptime(dataFimInscr, formatoString),
        "local": local,
        "vagas ofertadas": {
            "total vagas": vagasComNote + vagasSemNote,
            "vagas com notebook": vagasComNote,
            "vagas sem notebook": vagasSemNote,
            "vagas preenchidas": 0,
        },
        "carga horária": cargaHoraria,
        "valor": valor,
    }

