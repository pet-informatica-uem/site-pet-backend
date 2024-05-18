from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from src.modelos.excecao import APIExcecaoBase


class ExcecaoAPIMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except APIExcecaoBase as exc:
            return exc.response()
