from pathlib import Path
from pydantic import BaseModel

from src.modelos.inscrito.inscrito import Inscrito


class InscritoCriar(BaseModel):
    tipoVaga: bool
    "Tipo de vaga: True para com notebook e False para sem notebook."

    nivelConhecimento: int
    "Nível de conhecimento do usuário (1 a 5)."

    comprovante: Path | None = None
    "Comprovante de pagamento da inscrição."


class InscritoLer(Inscrito):
    pass


class InscritoAtualizar(BaseModel):
    tipoVaga: bool | None = None
    "Tipo de vaga: True para com notebook e False para sem notebook."

    comprovante: Path | None = None
    "Comprovante de pagamento da inscrição."


class InscritoDeletar(BaseModel):
    idEvento: str
    "Identificador único do evento."

    idUsuario: str
    "Identificador único do usuário."
