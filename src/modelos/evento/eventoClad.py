from datetime import datetime

from pydantic import BaseModel

from src.modelos.evento.evento import Evento


class EventoCriar(BaseModel):
    titulo: str
    "Título do evento."

    descricao: str
    "Descrição do evento."

    preRequisitos: list[str] = []
    "Pré requisitos para participar do evento."

    inicioInscricao: datetime

    fimInscricao: datetime

    dias: list[tuple[datetime, datetime]]

    local: str

    vagasComNote: int

    vagasSemNote: int

    cargaHoraria: int

    valor: float


class EventoLer(Evento):
    pass


class EventoAtualizar(BaseModel):
    titulo: str
    "Título do evento."

    descricao: str
    "Descrição do evento."

    preRequisitos: list[str]
    "Pré requisitos para participar do evento."

    inicioInscricao: datetime

    fimInscricao: datetime

    dias: list[tuple[datetime, datetime]]

    local: str

    vagasComNote: int

    vagasSemNote: int
    
    cargaHoraria: int

    valor: float


class EventoDeletar(BaseModel):
    id: str
