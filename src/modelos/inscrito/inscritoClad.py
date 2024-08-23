from pathlib import Path
from typing import Literal

from pydantic import BaseModel

from src.modelos.inscrito.inscrito import Inscrito, TipoVaga, NivelConhecimento


class InscritoCriar(BaseModel):
    tipoVaga: TipoVaga
    "Tipo de vaga: True para com notebook e False para sem notebook."

    nivelConhecimento: NivelConhecimento
    "Nível de conhecimento do usuário (1 a 5)."


class InscritoLer(Inscrito):
    pass


class InscritoAtualizar(BaseModel):
    tipoVaga: TipoVaga | None = None
    "Tipo de vaga: True para com notebook e False para sem notebook."


class InscritoDeletar(BaseModel):
    idEvento: str
    "Identificador único do evento."

    idUsuario: str
    "Identificador único do usuário."