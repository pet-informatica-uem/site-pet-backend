from datetime import datetime

from pydantic import BaseModel


class DadosEvento(BaseModel):
    nomeEvento: str
    resumo: str
    preRequisitos: str
    dataHoraEvento: datetime
    inicioInscricao: datetime
    fimInscricao: datetime
    local: str
    vagasComNote: int
    vagasSemNote: int
    cargaHoraria: int
    valor: float
    caminhoArteEvento: str = ""
    caminhoArteQrcode: str = ""

    def paraBD(self):
        modelBD = {
            "nome evento": self.nomeEvento,
            "resumo": self.resumo,
            "pré-requisitos": self.preRequisitos,
            "data/hora evento": self.dataHoraEvento,
            "data inicio inscrição": self.inicioInscricao,
            "data fim inscrição": self.fimInscricao,
            "local": self.local,
            "vagas ofertadas": {
                "vagas com notebook": self.vagasComNote,
                "vagas sem notebook": self.vagasSemNote,
            },
            "carga horária": self.cargaHoraria,
            "valor": self.valor,
            "arte evento": self.caminhoArteEvento,
            "arte qrcode": self.caminhoArteQrcode,
        }
        return modelBD


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
