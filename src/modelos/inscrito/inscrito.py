from datetime import datetime
from pathlib import Path

from pydantic import BaseModel


class Inscrito(BaseModel):
    """
    Classe que representa os inscritos de um evento.
    """

    idEvento: str
    "Identificador único do evento."

    idUsuario: str
    "Identificador único do usuário."

    tipoVaga: bool
    "Tipo de vaga: True para com notebook e False para sem notebook."

    nivelConhecimento: int
    "Nível de conhecimento do usuário (1 a 5)."

    comprovante: Path | None = None
    "Comprovante de pagamento da inscrição."

    dataInscricao: datetime
    "Data e hora da inscrição."
