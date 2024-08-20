from datetime import datetime
from typing import Self

from pydantic import BaseModel, ValidationInfo, field_validator, model_validator

from src.modelos.evento.evento import Evento, TipoVaga, NivelConhecimento


class EventoCriar(BaseModel):
    titulo: str

    descricao: str

    preRequisitos: list[str] = []

    inicioInscricao: datetime

    fimInscricao: datetime

    dias: list[tuple[datetime, datetime]]

    local: str

    vagasComNote: int

    vagasSemNote: int

    cargaHoraria: int

    valor: float

    @field_validator("dias")
    def diasValidos(
        cls, dias: list[tuple[datetime, datetime]]
    ) -> list[tuple[datetime, datetime]]:
        for i, dia in enumerate(dias):
            if dia[0] > dia[1]:
                raise ValueError(
                    f"A data de início do dia {i} deve ser anterior à data de fim do dia {i}."
                )

        return dias

    @model_validator(mode="after")
    def inscricoesValidas(self) -> Self:
        if self.inicioInscricao > self.fimInscricao:
            raise ValueError(
                "A data de início das inscrições deve ser anterior à data de fim das inscrições."
            )

        return self


class EventoLer(Evento):
    pass


class EventoAtualizar(BaseModel):
    titulo: str | None = None

    descricao: str | None = None

    preRequisitos: list[str] | None = None

    inicioInscricao: datetime | None = None

    fimInscricao: datetime | None = None

    dias: list[tuple[datetime, datetime]] | None = None

    local: str | None = None

    vagasComNote: int | None = None

    vagasSemNote: int | None = None

    cargaHoraria: int | None = None

    valor: float | None = None

    @field_validator("dias")
    def diasValidos(
        cls, dias: list[tuple[datetime, datetime]] | None
    ) -> list[tuple[datetime, datetime]] | None:
        if dias:
            for i, dia in enumerate(dias):
                if dia[0] > dia[1]:
                    raise ValueError(
                        f"A data de início do dia {i} deve ser anterior à data de fim do dia {i}."
                    )

        return dias

    @model_validator(mode="after")
    def inscricoesValidas(self) -> Self:
        if (
            self.inicioInscricao
            and self.fimInscricao
            and self.inicioInscricao > self.fimInscricao
        ):
            raise ValueError(
                "A data de início das inscrições deve ser anterior à data de fim das inscrições."
            )

        return self

class InscritoCriar(BaseModel):
    tipoVaga: TipoVaga
    "Tipo de vaga: True para com notebook e False para sem notebook."

    nivelConhecimento: NivelConhecimento
    "Nível de conhecimento do usuário (1 a 5)."


class InscritoLer(Evento): #PODE ESTAR ERRADO 
    pass


class InscritoAtualizar(BaseModel):
    tipoVaga: TipoVaga | None = None
    "Tipo de vaga: True para com notebook e False para sem notebook."


class InscritoDeletar(BaseModel):
    idEvento: str
    "Identificador único do evento."

    idUsuario: str
    "Identificador único do usuário."
