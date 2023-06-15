from pydantic import BaseModel, ValidationError, validator
from datetime import datetime


class DadosEvento(BaseModel):
    nomeEvento: str
    resumo: str
    preRequisitos: str
    dataHoraEvento: datetime
    inicioInscricao: datetime
    fimInscricao: datetime
    local: str
    vagasOfertadas: dict[str, int]
    cargaHoraria: int
    valor: int
    arteEvento: str
    arteQrcode: str = None

    @validator("vagasOfertadas")
    def validationVagasOfertadas(cls, v):
        keys = v.keys()
        if len(keys) == 2 and "comNote" in keys and "semNote" in keys:
            return v
        raise ValueError("Deve conter as chaves 'comNote' e 'semNote', apenas.")

    def dict(self):
        modelDict = {
            "nome evento": self.nomeEvento,
            "resumo": self.resumo,
            "pré-requisitos": self.preRequisitos,
            "data/hora evento": self.dataHoraEvento,
            "data inicio inscrição": self.inicioInscricao,
            "data fim inscrição": self.fimInscricao,
            "local": self.local,
            "vagas ofertadas": {
                "vagas com notebook": self.vagasOfertadas["comNote"],
                "vagas sem notebook": self.vagasOfertadas["semNote"],
            },
            "carga horária": self.cargaHoraria,
            "valor": self.valor,
            "arte evento": self.arteEvento,
            "arte qrcode": self.arteQrcode,
        }
        return modelDict


# dEven = DadosEvento(
#     nomeEvento="Evento",
#     resumo="Evento de teste",
#     preRequisitos="nenhum",
#     dataHoraEvento=datetime.now(),
#     inicioInscricao=datetime.now(),
#     fimInscricao=datetime.now(),
#     local="sala2",
#     vagasOfertadas={"comNote": 2, "semNote": 4},
#     cargaHoraria=20,
#     valor=20,
#     arteEvento="imagens/arte/evento.png",
#     arteQrcode="imagens/arte/evento.png",
# )

# print(dEven.dict())
