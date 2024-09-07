from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from src.modelos.excecao import APIExcecaoBase


class ExcecaoAPIMiddleware(BaseHTTPMiddleware):
    """
    Captura exceções cuja classe raiz é APIExcecaoBase e as converte
    em respostas JSON.
    """
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except APIExcecaoBase as exc:
            return exc.response()
