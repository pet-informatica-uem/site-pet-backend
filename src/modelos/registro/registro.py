from datetime import datetime
from pydantic import BaseModel


class Registro(BaseModel):

    idUsuario: str
    "Identificador único."

    ipUsuario: str
    "Endereço IP do usuário."

    dataHora: datetime
    "Data e hora do login."

    sucesso: bool
    "Indica se o login foi bem sucedido."
