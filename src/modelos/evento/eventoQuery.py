from enum import Enum


class eventoQuery(str, Enum):
    PASSADO = "passados"
    PRESENTE = "atuais"
    FUTURO = "futuros"
    TODOS = "todos"
