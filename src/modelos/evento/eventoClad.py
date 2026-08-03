from datetime import datetime
from typing import Self

from pydantic import BaseModel, ValidationInfo, field_validator, model_validator

from src.modelos.evento.enums import TipoVaga, TipoEvento, NivelConhecimento
from src.modelos.evento.evento import Evento, Inscrito
from src.modelos.evento.validacaoEvento import ValidacaoEvento


class EventoCriar(BaseModel):
    """
    Dados de um pedido de criação de evento no sistema.
    """

    titulo: str
    """Título do evento."""

    tipoEvento: TipoEvento
    """Categoria do evento."""

    descricao: str
    """Descrição do evento."""

    preRequisitos: str
    """Pré-requisitos para participar do evento."""

    inicioInscricao: datetime
    """Data e hora de início das inscrições."""

    fimInscricao: datetime
    """Data e hora de fim das inscrições."""

    dias: list[tuple[datetime, datetime]]
    """Lista de tuplas de data e hora de início e fim de cada dia do evento."""

    local: str
    """Local do evento."""

    vagasComNote: int
    """Quantidade de vagas com notebook."""

    vagasSemNote: int
    """Quantidade de vagas sem notebook."""

    cargaHoraria: int
    """Carga horária do evento."""

    chavePIX: str | None = None
    """Chave PIX para pagamento."""

    valor: float
    """Valor da inscrição."""

    organizadores: list[str] = []
    """Identificadores dos petianos responsáveis pela organização do evento."""

    @field_validator("dias")
    def dias_valido(cls, v: list[tuple[datetime, datetime]]):
        """
        Valida o campo de dias
        """
        # Para essa validação, as exceções das verificações são tratadas internamente.
        ValidacaoEvento.diasValidos(v)
        return v
    
    @field_validator("valor")
    def valor_valido(cls, v: float):
        """
        Valida o campo de valor
        """
        if not ValidacaoEvento.valorValido(v):
            raise ValueError("Valor de custo de inscrição inválido.")
        return v

    @model_validator(mode='after')
    def data_inscricao_valida(self) -> Self:
        """
        Valida os campos de início de inscrição e fim de inscrição
        """
        if not ValidacaoEvento.inscricoesValidas(self.inicioInscricao, self.fimInscricao):
            raise ValueError("Datas de prazo de inscrição inválidas.")
        return self


class EventoLerAdmin(Evento):
    titulo: str | None = None
    """Título do evento."""

    tipoEvento: TipoEvento | None = None
    """Categoria do evento."""

    descricao: str | None = None
    """Descrição do evento."""

    preRequisitos: str | None = None
    """Pré-requisitos para participar do evento."""

    inicioInscricao: datetime | None = None
    """Data e hora de início das inscrições."""

    fimInscricao: datetime | None = None
    """Data e hora de fim das inscrições."""

    dias: list[tuple[datetime, datetime]] | None = None
    """Lista de tuplas de data e hora de início e fim de cada dia do evento."""

    local: str | None = None
    """Local do evento."""

    vagasComNote: int | None = None
    """Quantidade de vagas com notebook."""

    vagasSemNote: int | None = None
    """Quantidade de vagas sem notebook."""

    cargaHoraria: int | None = None
    """Carga horária do evento."""

    chavePIX: str | None = None
    """Chave PIX para pagamento."""

    valor: float | None = None
    """Valor da inscrição."""


class EventoLer(Evento):
    titulo: str | None = None
    """Título do evento."""

    descricao: str | None = None
    """Descrição do evento."""

    preRequisitos: str | None = None
    """Pré-requisitos para participar do evento."""

    inicioInscricao: datetime | None = None
    """Data e hora de início das inscrições."""

    fimInscricao: datetime | None = None
    """Data e hora de fim das inscrições."""

    dias: list[tuple[datetime, datetime]] | None = None
    """Lista de tuplas de data e hora de início e fim de cada dia do evento."""

    local: str | None = None
    """Local do evento."""

    cargaHoraria: int | None = None
    """Carga horária do evento."""

    chavePIX: str | None = None
    """Chave PIX para pagamento."""

    valor: float | None = None
    """Valor da inscrição."""



class EventoAtualizarAdmin(BaseModel):
    """
    Dados de um pedido de atualização de um evento no sistema.
    """
    
    titulo: str | None = None
    """Título do evento."""

    tipoEvento: TipoEvento | None = None
    """Categoria do evento."""

    descricao: str | None = None
    """Descrição do evento."""

    preRequisitos: str | None = None
    """Pré-requisitos para participar do evento."""

    inicioInscricao: datetime | None = None
    """Data e hora de início das inscrições."""

    fimInscricao: datetime | None = None
    """Data e hora de fim das inscrições."""

    dias: list[tuple[datetime, datetime]] | None = None
    """Lista de tuplas de data e hora de início e fim de cada dia do evento."""

    local: str | None = None
    """Local do evento."""

    vagasComNote: int | None = None
    """Quantidade de vagas com notebook."""

    vagasSemNote: int | None = None
    """Quantidade de vagas sem notebook."""

    cargaHoraria: int | None = None
    """Carga horária do evento."""

    chavePIX: str | None = None
    """Chave PIX para pagamento."""

    valor: float | None = None
    """Valor da inscrição."""

    organizadores: list[str] | None = None
    """Identificadores dos petianos responsáveis pela organização do evento."""


class InscritoCriar(BaseModel):
    """
    Criação de um inscrito no evento.
    """

    comprovante: str | None = None
    """Comprovante de pagamento anexado pelo inscrito."""

    estadoDeVerificacao: bool | None = None
    """Indica se o comprovante de pagamento anexado foi verificado."""

    tipoVaga: TipoVaga
    """Indica se o inscrito utilizará ou não o próprio notebook no evento."""

    nivelConhecimento: NivelConhecimento
    """Nível de conhecimento do usuário (1 a 5)."""


class InscritoLer(Inscrito):
    """
    Informações sobre uma inscrição em um evento.
    """

    nome: str
    """Nome do usuário inscrito."""

    cpf: str
    """CPF do usuário inscrito."""

    email: str
    """E-mail do usuário inscrito."""

    curso: str | None = None
    """Curso do usuário inscrito."""

    comprovante: str | None = None
    """Comprovante de pagamento anexado pelo inscrito."""

    estadoDeVerificacao: bool | None = None
    """Indica se o comprovante de pagamento anexado foi verificado."""

    tipoVaga: TipoVaga
    """Indica se o inscrito utilizará ou não o próprio notebook no evento."""

    nivelConhecimento: NivelConhecimento
    """Nível de conhecimento do usuário (1 a 5)."""


class InscritoAtualizar(BaseModel):
    """
    Atualiza um dado em um inscrito no evento.
    """

    comprovante: str | None = None
    """Comprovante de pagamento anexado pelo inscrito."""

    estadoDeVerificacao: bool | None = None
    """Indica se o comprovante de pagamento anexado foi verificado."""

    tipoVaga: TipoVaga
    """Indica se o inscrito utilizará ou não o próprio notebook no evento."""

    nivelConhecimento: NivelConhecimento
    """Nível de conhecimento do usuário (1 a 5)."""


class VerificacaoInscricao(BaseModel):
    """Decisão de um petiano sobre o comprovante de uma inscrição."""

    estadoDeVerificacao: bool
    """Verdadeiro para aceitar e falso para rejeitar o comprovante."""
