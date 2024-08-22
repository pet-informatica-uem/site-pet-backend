from enum import Enum


class eventoQuery(str, Enum):
    """
    Classe que utiliza tipos enumerados para representar o estado de um evento.
    """

    PASSADO = "passados"
    PRESENTE = "atuais"
    FUTURO = "futuros"
    TODOS = "todos"
