from datetime import datetime

from pydantic import BaseModel


class RegistroLogin(BaseModel):
    """
    Dados do registro de login de um usuário.
    """

    emailUsuario: str
    "E-mail do usuário."

    ipUsuario: str
    "Endereço IP do usuário."

    dataHora: datetime
    "Data e hora do login."

    sucesso: bool
    "Indica se o login foi bem sucedido."

    motivo: str = ""
    "Em caso de falha, o motivo do erro."
