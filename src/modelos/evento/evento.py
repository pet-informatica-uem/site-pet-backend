from datetime import datetime
from src.modelos.evento.enums import TipoVaga, TipoEvento, NivelConhecimento
from pydantic import BaseModel, Field
from bson.objectid import ObjectId
from uuid import uuid4


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

    tipoEvento: TipoEvento
    "Categoria do evento."

    descricao: str
    "Descrição do evento."

    preRequisitos: str
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

    chavePIX: str | None = None
    "Chave PIX para pagamento"

    valor: float
    "Valor da inscrição."

    capa: str | None = None
    "Caminho para a imagem de capa do evento."

    cracha: str | None = None
    "Caminho para a imagem do crachá do evento."


    class Config:
        popula_por_nome = True  # Permite usar alias ao popular campos
        json_encoders = {datetime: lambda v: v.isoformat()}  # Serializa datetimes corretamente
