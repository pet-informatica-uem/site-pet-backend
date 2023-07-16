from fastapi import status
from fastapi.responses import JSONResponse

from src.modelos.erros import ErroBase, JaExisteErro

from typing import Type


class APIExcecaoBase(Exception):
    message = "Erro genérico."
    code = status.HTTP_500_INTERNAL_SERVER_ERROR
    model = ErroBase

    def __init__(self, **kwargs):
        kwargs.setdefault("message", self.message)
        self.message = kwargs["message"]
        self.data = self.model(**kwargs)

    def response(self):
        return JSONResponse(content=self.data.dict(), status_code=self.code)

    @classmethod
    def response_model(cls):
        return {cls.code: {"model": cls.model}}


class JaExisteExcecao(APIExcecaoBase):
    message = "A entidade já existe."
    code = status.HTTP_409_CONFLICT
    model = JaExisteErro


class UsuarioJaExisteExcecao(JaExisteExcecao):
    message = "O usuário já existe."


def get_exception_responses(*args: Type[APIExcecaoBase]) -> dict:
    """Given BaseAPIException classes, return a dict of responses used on FastAPI endpoint definition, with the format:
    {statuscode: schema, statuscode: schema, ...}"""
    responses = dict()
    for cls in args:
        responses.update(cls.response_model())
    return responses
