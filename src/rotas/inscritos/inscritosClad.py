from pydantic import BaseModel

from modelos.inscritos.inscritos import Inscrito


class InscritosCriar(BaseModel):
    """
    Classe que representa os inscritos de um evento.
    """

    idEvento: str
    "Identificador único do evento."

    vagasDisponiveisComNote: int
    "Número de vagas com notebook."

    vagasDisponiveisSemNote: int
    "Número de vagas sem notebook."


class InscritosLer(BaseModel):
    """
    Classe que representa os inscritos de um evento.
    """

    inscritos: list[Inscrito]
    "Lista de inscritos."

    vagasDisponiveisComNote: int
    "Número de vagas com notebook."

    vagasDisponiveisSemNote: int
    "Número de vagas sem notebook."


class InscritosAtualizar(InscritosLer):
    pass


class InscritosDeletar(BaseModel):
    """
    Classe que representa os inscritos de um evento.
    """

    idEvento: str
    "Identificador único do evento."
