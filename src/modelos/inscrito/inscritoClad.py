from pathlib import Path

from pydantic import BaseModel

from src.modelos.inscrito.inscrito import Inscrito

from enum import Enum

class TipoVaga(str, Enum):
    COM_NOTE = "comNotebook"
    SEM_NOTE = "semNotebook"

class InscritoCriar(BaseModel):
    tipoVaga: TipoVaga
    "Tipo de vaga: True para com notebook e False para sem notebook."

    nivelConhecimento: int
    "Nível de conhecimento do usuário (1 a 5)."


class InscritoLer(Inscrito):
    pass


class InscritoAtualizar(BaseModel):
    tipoVaga: bool | None = None
    "Tipo de vaga: True para com notebook e False para sem notebook."


class InscritoDeletar(BaseModel):
    idEvento: str
    "Identificador único do evento."

    idUsuario: str
    "Identificador único do usuário."
