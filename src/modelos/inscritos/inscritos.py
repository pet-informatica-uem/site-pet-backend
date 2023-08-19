from datetime import datetime
from pathlib import Path
from pydantic import BaseModel

from src.modelos.inscritos.inscrito import Inscrito


class Inscritos(BaseModel):
    """
    Classe que representa os inscritos de um evento.
    """

    idEvento: str
    "Identificador único do evento."

    inscritos: list[Inscrito]
    "Lista de identificadores dos inscritos com notebook."

    vagasDisponiveisComNote: int
    "Número de vagas com notebook."

    vagasDisponiveisSemNote: int
    "Número de vagas sem notebook."
