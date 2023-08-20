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
    titulo: str | None = None
    "Título do evento."

    descricao: str | None = None
    "Descrição do evento."

    preRequisitos: list[str] | None = None
    "Pré requisitos para participar do evento."

    inicioInscricao: datetime | None = None

    fimInscricao: datetime | None = None

    dias: list[tuple[datetime, datetime]] | None = None

    local: str | None = None

    vagasComNote: int | None = None

    vagasSemNote: int | None = None

    cargaHoraria: int | None = None

    valor: float | None = None


class EventoDeletar(BaseModel):
    id: str
