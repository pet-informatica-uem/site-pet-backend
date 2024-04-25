from enum import Enum

class eventoQuery(str, Enum):
    PASSADO = 'passados'
    PRESENTE = 'presente'
    FUTURO = 'futuros'