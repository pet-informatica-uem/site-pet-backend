from typing import TypedDict

class Inscricao(TypedDict):
    idEvento: str
    idUsuario: str
    nivelConhecimento: str
    tipoInscricao: str
    pagamento: bool

class VagasEvento(TypedDict):
    idEvento: str
    vagasComNotebook: int
    vagasSemNotebook: int
    vagasPreenchidasComNotebook: int
    vagasPreenchidasSemNotebook: int