from enum import Enum


class IntervaloBusca(str, Enum):
    """
    Determina o intervalo de tempo em que eventos podem ser recuperados.
    """

    PASSADO = "passados"
    """Eventos que já ocorreram."""

    PRESENTE = "atuais"
    """Eventos que estão ocorrendo no momento."""

    FUTURO = "futuros"
    """Eventos que ocorrerão no futuro."""

    TODOS = "todos"
    """Todos os eventos."""
