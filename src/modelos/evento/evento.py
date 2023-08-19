from datetime import datetime
from pathlib import Path

from pydantic import BaseModel, Field


# acho que precisa colocar um id aqui
class Evento(BaseModel):
    """
    Classe que representa um evento do sistema.
    """

    id: str = Field(..., alias="_id")
    "Identificador único."

    titulo: str
    "Título do evento."

    descricao: str
    "Descrição do evento."

    preRequisitos: list[str]
    "Pré requisitos para participar do evento."

    inicioInscricao: datetime

    fimInscricao: datetime

    dias: list[tuple[datetime, datetime]]

    local: str

    vagasComNote: int

    vagasSemNote: int

    cargaHoraria: int

    valor: float

    imagemCapa: Path | None = None

    imagemCracha: Path | None = None
