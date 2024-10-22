from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class TipoVaga(str, Enum):
    """
    Determina se o inscrito utilizará ou não o próprio notebook durante o evento.
    """

    COM_NOTE = "comNotebook"
    SEM_NOTE = "semNotebook"


class NivelConhecimento(str, Enum):
    """
    Determina o nível de conhecimento de um inscrito a respeito do tema do evento, em uma escala de 1 a 5.
    """

    NENHUM = "1"
    BASICO = "2"
    INTERMEDIARIO = "3"
    AVANCADO = "4"
    ESPECIALISTA = "5"


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
