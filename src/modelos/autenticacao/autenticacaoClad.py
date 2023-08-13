from datetime import datetime
from pydantic import BaseModel, Field
from src.modelos.excecao import NaoEncontradoExcecao

from src.modelos.bd import colecaoTokens


class TokenAutenticacao(BaseModel):
    id: str = Field(..., alias="_id")
    idUsuario: str
    validade: datetime


class TokenAutenticacaoClad:
    @staticmethod
    def get(id: str) -> TokenAutenticacao:
        documento = colecaoTokens.find_one({"_id": id})
        if not documento:
            raise NaoEncontradoExcecao()

        return TokenAutenticacao(**documento)

    @staticmethod
    def deletar(id: str):
        resultado = colecaoTokens.delete_one({"_id": id})
        if resultado.deleted_count != 1:
            raise NaoEncontradoExcecao()

    @staticmethod
    def criar(id: str, idUsuario: str, validade: datetime) -> TokenAutenticacao:
        documento = {"_id": id, "idUsuario": idUsuario, "validade": validade}

        resultado = colecaoTokens.insert_one(documento)
        assert resultado.acknowledged

        return TokenAutenticacaoClad.get(str(resultado.inserted_id))

    @staticmethod
    def deletarTokensUsuario(idUsuario: str):
        colecaoTokens.delete_many({"idUsuario": idUsuario})
