from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
from bson.objectid import ObjectId
from uuid import uuid4

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
    idUsuario: str = Field(..., alias="_id")
    tipoVaga: TipoVaga
    nivelConhecimento: NivelConhecimento | None = None
    comprovante: str | None = None
    dataHoraInscricao: datetime

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
    "Pré-requisitos para participar do evento."

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

    inscritos: list[Inscrito] = []
    "Pessoas inscritas no evento."

    cargaHoraria: int
    "Carga horária do evento."

    valor: float
    "Valor da inscrição."

    arte: str | None = None
    "Caminho para a imagem de capa do evento."

    cracha: str | None = None
    "Caminho para a imagem do crachá do evento."

    class Config:
        allow_population_by_field_name = True  # Permite usar alias ao popular campos
        json_encoders = {datetime: lambda v: v.isoformat()}  # Serializa datetimes corretamente
