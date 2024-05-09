from enum import Enum

class EventoQuery(str, Enum):
    PASSADO = 'passados'
    PRESENTE = 'atuais'
    FUTURO = 'futuros'
    TODOS = 'todos'