"""
Modelos de dados relacionados a inscritos em eventos.
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class TipoVaga(str, Enum):
    """
    Determina se o inscrito utilizará ou não o próprio notebook durante o evento.
    """

    COM_NOTE = "comNotebook"
    """Utilizará o próprio notebook."""

    SEM_NOTE = "semNotebook"
    """Não utilizará o próprio notebook."""


class NivelConhecimento(str, Enum):
    """
    Determina o nível de conhecimento de um inscrito a respeito do tema do evento, em uma escala de 1 a 5.
    """

    NENHUM = "1"
    """Não possui conhecimento prévio."""

    BASICO = "2"
    """Possui conhecimento básico."""

    INTERMEDIARIO = "3"
    """Possui conhecimento intermediário."""

    AVANCADO = "4"
    """Possui conhecimento avançado."""

    ESPECIALISTA = "5"
    """Domina o assunto."""


class Inscrito(BaseModel):
    """
    Dados de um inscrito em um evento.
    """

    idEvento: str
    "Identificador único do evento."

    idUsuario: str
    "Identificador único do usuário."

    tipoVaga: TipoVaga
    "Indica se o inscrito utilizará ou não o próprio notebook no evento."

    nivelConhecimento: NivelConhecimento
    "Nível de conhecimento do usuário."

    comprovante: str | None = None
    "Comprovante de pagamento da inscrição."

    dataInscricao: datetime
    "Data e hora da inscrição."
