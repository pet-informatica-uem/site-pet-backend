"""
Modelos de dados relacionados ao CRUD de inscrições em eventos.
"""

from pathlib import Path
from typing import Literal

from pydantic import BaseModel

from src.modelos.inscrito.inscrito import Inscrito, TipoVaga, NivelConhecimento


class InscritoCriar(BaseModel):
    """
    Criação de um inscrito no evento.
    """

    tipoVaga: TipoVaga
    "Tipo de vaga: True para com notebook e False para sem notebook."

    nivelConhecimento: NivelConhecimento
    "Nível de conhecimento do usuário (1 a 5)."


class InscritoLer(Inscrito):
    """
    Informações sobre uma inscrição em um evento.
    """
    pass


class InscritoAtualizar(BaseModel):
    """
    Atualiza um dado em um inscrito no evento.
    """

    tipoVaga: TipoVaga | None = None
    "Tipo de vaga: True para com notebook e False para sem notebook."


class InscritoDeletar(BaseModel):
    """
    Deleta um inscrito de um evento.
    """
    
    idEvento: str
    "Identificador único do evento."

    idUsuario: str
    "Identificador único do usuário."
