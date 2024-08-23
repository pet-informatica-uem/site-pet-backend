from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class TipoVaga(str, Enum):
    COM_NOTE = "comNotebook"
    SEM_NOTE = "semNotebook"


class NivelConhecimento(str, Enum):
    NENHUM = "1"
    BASICO = "2"
    INTERMEDIARIO = "3"
    AVANCADO = "4"
    ESPECIALISTA = "5"


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

    comprovante: str | None = None
    "Comprovante de pagamento da inscrição."

    dataInscricao: datetime
    "Data e hora da inscrição."