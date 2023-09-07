from datetime import datetime
from enum import Enum
from pathlib import Path

from pydantic import BaseModel


class TipoVaga(str, Enum):
    COM_NOTE = "comNotebook"
    SEM_NOTE = "semNotebook"


class Inscrito(BaseModel):
    """
    Classe que representa os inscritos de um evento.
    """

    idEvento: str
    "Identificador único do evento."

    idUsuario: str
    "Identificador único do usuário."

    tipoVaga: TipoVaga
    "Tipo de vaga: True para com notebook e False para sem notebook."

    nivelConhecimento: int
    "Nível de conhecimento do usuário (1 a 5)."

    comprovante: Path | None = None
    "Comprovante de pagamento da inscrição."

    dataInscricao: datetime
    "Data e hora da inscrição."
