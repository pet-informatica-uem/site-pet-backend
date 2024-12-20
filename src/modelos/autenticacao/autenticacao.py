from datetime import datetime

from pydantic import BaseModel, Field


class TokenAutenticacao(BaseModel):
    """
    Um token de autenticação.
    """

    id: str = Field(..., alias="_id")
    "Identificador do token."

    idUsuario: str
    "Identificador do usuário."

    validade: datetime
    "Data de validade do token."
