from datetime import datetime
from typing import Self

from pydantic import BaseModel, field_validator, Field, model_validator

from src.modelos.evento.evento import Evento


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
    # id requerido por causa do seguinte bug
    # https://github.com/pydantic/pydantic/issues/1869
    
    id: str
    "Identificador único."
    
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
