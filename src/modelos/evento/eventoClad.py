from datetime import datetime
from typing import Self

from pydantic import BaseModel, ValidationInfo, field_validator, model_validator

from src.modelos.evento.evento import Evento


class EventoCriar(BaseModel):
    """
    Classe que representa um evento do sistema.
    """

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

    local: str
    "Local do evento."

    vagasComNote: int
    "Quantidade de vagas com notebook."

    vagasSemNote: int
    "Quantidade de vagas sem notebook."

    cargaHoraria: int
    "Carga horária do evento."

    valor: float
    "Valor da inscrição."

    @field_validator("dias")
    def diasValidos(
        cls, dias: list[tuple[datetime, datetime]]
    ) -> list[tuple[datetime, datetime]]:
        """
        Função para verificar se as datas de início e fim de cada dia do evento são válidas.
            :cls: EventoCriar -> referência à classe EventoCriar, na qual o método está sendo definido.
            :dias: list[tuple[datetime, datetime]] -> a data e a hora de início e fim de cada dia do evento.
        """
        for i, dia in enumerate(dias):
            if dia[0] > dia[1]:
                raise ValueError(
                    f"A data de início do dia {i} deve ser anterior à data de fim do dia {i}."
                )

        return dias

    @model_validator(mode="after")
    def inscricoesValidas(self) -> Self:
        """
        Função para verificar se as datas das inscrições do evento são válidas.
            :self: EventoCriar -> referência à classe EventoCriar, na qual o método está sendo definido.
        """
        if self.inicioInscricao > self.fimInscricao:
            raise ValueError(
                "A data de início das inscrições deve ser anterior à data de fim das inscrições."
            )

        return self


class EventoLer(Evento):
    pass


class EventoAtualizar(BaseModel):
    """
    Classe que representa a atualização de um evento do sistema.
    """
    
    titulo: str | None = None
    "Título do evento."

    descricao: str | None = None
    "Descrição do evento."

    preRequisitos: list[str] | None = None
    "Pré requisitos para participar do evento."

    inicioInscricao: datetime | None = None
    "Data e hora de início das inscrições."

    fimInscricao: datetime | None = None
    "Data e hora de fim das inscrições."

    dias: list[tuple[datetime, datetime]] | None = None
    "Lista de tuplas de data e hora de início e fim de cada dia do evento."

    local: str | None = None
    "Local do evento."

    vagasComNote: int | None = None
    "Quantidade de vagas com notebook."

    vagasSemNote: int | None = None
    "Quantidade de vagas sem notebook."

    cargaHoraria: int | None = None
    "Carga horária do evento."

    valor: float | None = None
    "Valor da inscrição."

    @field_validator("dias")
    def diasValidos(
        cls, dias: list[tuple[datetime, datetime]] | None
    ) -> list[tuple[datetime, datetime]] | None:
        """
        Função para verificar se as datas a serem atualizar de início e fim de cada dia do evento são válidas.
            :cls: EventoCriar -> referência à classe EventoCriar, na qual o método está sendo definido.
            :dias: list[tuple[datetime, datetime]] -> a data e a hora de início e fim de cada dia do evento.
        """
        if dias:
            for i, dia in enumerate(dias):
                if dia[0] > dia[1]:
                    raise ValueError(
                        f"A data de início do dia {i} deve ser anterior à data de fim do dia {i}."
                    )

        return dias

    @model_validator(mode="after")
    def inscricoesValidas(self) -> Self:
        """
        Função para verificar se as datas a serem atualizadas das inscrições do evento são válidas.
            :self: EventoCriar -> referência à classe EventoCriar, na qual o método está sendo definido.
        """
        if (
            self.inicioInscricao
            and self.fimInscricao
            and self.inicioInscricao > self.fimInscricao
        ):
            raise ValueError(
                "A data de início das inscrições deve ser anterior à data de fim das inscrições."
            )

        return self
