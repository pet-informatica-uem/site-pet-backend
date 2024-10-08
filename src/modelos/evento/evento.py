from datetime import datetime

from pydantic import BaseModel, Field


class Evento(BaseModel):
    """
    Classe que representa um evento do sistema.
    """

    id: str = Field(..., alias="_id")
    "Identificador único."

    titulo: str
    "Título do evento."

    descricao: str
    "Descrição do evento."

    preRequisitos: list[str] = []
    "Pré requisitos para participar do evento."

    inicioInscricao: datetime
    "Data e hora de início das inscrições."

    fimInscricao: datetime
    "Data e hora de fim das inscrições."

    dias: list[tuple[datetime, datetime]]
    "Lista de tuplas de data e hora de início e fim de cada dia do evento."

    inicioEvento: datetime
    "Primeiro dia e hora do evento (gerado automaticamente a partir de 'dias')."

    fimEvento: datetime
    "Último dia e hora do evento (gerado automaticamente a partir de 'dias')."

    local: str
    "Local do evento."

    vagasComNote: int
    "Quantidade de vagas com notebook."

    vagasSemNote: int
    "Quantidade de vagas sem notebook."

    vagasDisponiveisComNote: int
    "Quantidade de vagas com notebook disponíveis."

    vagasDisponiveisSemNote: int
    "Quantidade de vagas sem notebook disponíveis."

    cargaHoraria: int
    "Carga horária do evento."

    valor: float
    "Valor da inscrição."

    arte: str | None = None
    "Caminho para a imagem de capa do evento."

    cracha: str | None = None
    "Caminho para a imagem do crachá do evento."
