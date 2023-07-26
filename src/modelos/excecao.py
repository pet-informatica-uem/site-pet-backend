from fastapi import status
from fastapi.responses import JSONResponse

from src.modelos.erros import ErroBase, JaExisteErro, NaoAutenticadoErro, NaoEncontradoErro

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
    
class ImagemInvalidaExcecao(APIExcecaoBase):
    message = "A foto não é válida."
    code = status.HTTP_400_BAD_REQUEST

class NaoAutenticadoExcecao(APIExcecaoBase):
    message = "Usuário não autenticado."
    code = status.HTTP_401_UNAUTHORIZED
    model = NaoAutenticadoErro

class NaoEncontradoExcecao(APIExcecaoBase):
    message = "A entidade não foi encontrada."
    code = status.HTTP_404_NOT_FOUND
    model = NaoEncontradoErro

class UsuarioNaoEncontradoExcecao(NaoEncontradoExcecao):
    message = "O usuário não foi encontrado."

class JaExisteExcecao(APIExcecaoBase):
    message = "A entidade já existe."
    code = status.HTTP_409_CONFLICT
    model = JaExisteErro


class UsuarioJaExisteExcecao(JaExisteExcecao):
    message = "O usuário já existe."


def listaRespostasExcecoes(*args: Type[APIExcecaoBase]) -> dict:
    """Given BaseAPIException classes, return a dict of responses used on FastAPI endpoint definition, with the format:
    {statuscode: schema, statuscode: schema, ...}"""
    respostas = dict()
    for cls in args:
        respostas.update(cls.response_model())
    return respostas