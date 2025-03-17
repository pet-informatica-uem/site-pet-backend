from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
from bson.objectid import ObjectId
from uuid import uuid4

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

    idUsuario: str
    "Identificador único do usuário."

    tipoVaga: TipoVaga
    "Indica se o inscrito utilizará ou não o próprio notebook no evento."

    nivelConhecimento: NivelConhecimento | None = None
    "Nível de conhecimento do usuário."

    comprovante: str | None = None
    "Comprovante de pagamento da inscrição."

    dataInscricao: datetime
    "Data e hora da inscrição."

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
        populate_by_name = True  # Permite usar alias ao popular campos
        json_encoders = {datetime: lambda v: v.isoformat()}  # Serializa datetimes corretamente
