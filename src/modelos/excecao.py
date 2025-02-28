from typing import Any, Type

from fastapi import status
from fastapi.responses import JSONResponse

from src.modelos.erros import (
    AcaoNaoCompletaErro,
    ErroBase,
    JaExisteErro,
    NaoAutenticadoErro,
    NaoAutorizadoErro,
    NaoEncontradoErro,
)


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

    def __str__(self):
        return self.message


class ImagemInvalidaExcecao(APIExcecaoBase):
    message = "A foto não é válida."
    code = status.HTTP_400_BAD_REQUEST


class ImagemNaoSalvaExcecao(APIExcecaoBase):
    message = "Erro no processamento da imagem."
    code = status.HTTP_500_INTERNAL_SERVER_ERROR


class NaoAutenticadoExcecao(APIExcecaoBase):
    message = "Usuário não autenticado."
    code = status.HTTP_401_UNAUTHORIZED
    model = NaoAutenticadoErro


class EmailSenhaIncorretoExcecao(APIExcecaoBase):
    message = "Email e/ou senha incorreto(s)."
    code = status.HTTP_401_UNAUTHORIZED


class EmailNaoConfirmadoExcecao(APIExcecaoBase):
    message = "Email não confirmado."
    code = status.HTTP_401_UNAUTHORIZED


class ForaDoPeriodoDeInscricaoExcecao(APIExcecaoBase):
    message = "Fora do período de inscrição."
    code = status.HTTP_400_BAD_REQUEST


class NaoAutorizadoExcecao(APIExcecaoBase):
    message = "Acesso negado."
    code = status.HTTP_403_FORBIDDEN
    model = NaoAutorizadoErro


class NaoEncontradoExcecao(APIExcecaoBase):
    message = "A entidade não foi encontrada."
    code = status.HTTP_404_NOT_FOUND
    model = ErroBase


class UsuarioNaoEncontradoExcecao(NaoEncontradoExcecao):
    message = "O usuário não foi encontrado."


class JaExisteExcecao(APIExcecaoBase):
    message = "A entidade já existe."
    code = status.HTTP_409_CONFLICT
    model = JaExisteErro


class ErroInternoExcecao(APIExcecaoBase):
    message = "Ocorreu um erro interno."
    code = status.HTTP_500_INTERNAL_SERVER_ERROR
    model = ErroBase


class ErroValidacaoExcecao(APIExcecaoBase):
    message = "Ocorreu um erro de validação."
    code = status.HTTP_400_BAD_REQUEST
    model = ErroBase


class NaoAtualizadaExcecao(APIExcecaoBase):  # conflito
    message = "Não foi possível atualizar."
    code = status.HTTP_404_NOT_FOUND
    model = AcaoNaoCompletaErro


class ErroNaAlteracaoExcecao(APIExcecaoBase):  # conflito
    message = "Não foi possível fazer a alteração."
    code = status.HTTP_404_NOT_FOUND
    model = AcaoNaoCompletaErro


class ComprovanteObrigatorioExcecao(APIExcecaoBase):  # conflito
    message = "Comprovante obrigatório para eventos pagos."
    code = status.HTTP_400_BAD_REQUEST
    model = AcaoNaoCompletaErro

class ComprovanteInvalido(APIExcecaoBase):  # conflito
    message = "Comprovante inválido."
    code = status.HTTP_400_BAD_REQUEST
    model = AcaoNaoCompletaErro


class ForaDoPeriodoDeInscricaoExcecao(APIExcecaoBase):  # conflito
    message = "Fora do período de inscrição."
    code = status.HTTP_423_LOCKED
    model = AcaoNaoCompletaErro


class SemVagasDisponiveisExcecao(APIExcecaoBase):  # conflito
    message = "Não há vagas disponíveis."
    code = status.HTTP_409_CONFLICT
    model = AcaoNaoCompletaErro


class TipoVagaInvalidoExcecao(APIExcecaoBase):  # conflito
    message = "Tipo de vaga inválido."
    code = status.HTTP_404_NOT_FOUND
    model = NaoEncontradoErro


class EmailNaoFoiEnviadoExcecao(APIExcecaoBase):
    message = "Não foi possível enviar o email"
    code = status.HTTP_500_INTERNAL_SERVER_ERROR
    model = AcaoNaoCompletaErro


class TipoDeInscricaoErradoExcecao(APIExcecaoBase):
    message = "Tipo de inscrição errada, deveria ser <com notebook> ou <sem notebook>"
    code = status.HTTP_400_BAD_REQUEST
    model = AcaoNaoCompletaErro


class NivelDeConhecimentoErradoExcecao(APIExcecaoBase):
    message = "Nivel de conhecimento inválido. Valores válidos são 1, 2, 3, 4 ou 5"
    code = status.HTTP_400_BAD_REQUEST
    model = AcaoNaoCompletaErro


class TokenInvalidoExcecao(APIExcecaoBase):
    message = "O token é inválido."
    code = status.HTTP_400_BAD_REQUEST


class TamanhoLimiteExcedidoExcecao(APIExcecaoBase):
    message = "O tamanho da requisição ultrapassou o limite."
    code = status.HTTP_413_REQUEST_ENTITY_TOO_LARGE


class TempoLimiteExcedidoExcecao(APIExcecaoBase):
    message = "Tempo limite excedido."
    code = status.HTTP_408_REQUEST_TIMEOUT


def listaRespostasExcecoes(
    *args: Type[APIExcecaoBase],
) -> dict[int | str, dict[str, Any]]:
    """Given BaseAPIException classes, return a dict of responses used on FastAPI endpoint definition, with the format:
    {statuscode: schema, statuscode: schema, ...}"""
    respostas = dict()
    for cls in args:
        respostas.update(cls.response_model())
    return respostas
