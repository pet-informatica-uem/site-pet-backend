from datetime import datetime
from pathlib import Path
from pydantic import BaseModel


class Inscrito(BaseModel):
    idUsuario: str
    "Identificador único do usuário."

    tipoVaga: bool
    "Tipo de vaga escolhida pelo usuário."

    nivelConhecimento: int
    "Nível de conhecimento do usuário."

    dataHora: datetime
    "Data e hora da inscrição."

    comprovante: Path | None = None
    "Comprovante de pagamento."


class InscritoCriar(Inscrito):
    tipoVaga: bool
    "Tipo de vaga escolhida pelo usuário."

    nivelConhecimento: int
    "Nível de conhecimento do usuário."

    comprovante: Path | None = None
    "Comprovante de pagamento."