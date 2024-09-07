import anyio
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from src.modelos.excecao import TempoLimiteExcedidoExcecao

REQUEST_TIMEOUT = 30
"Valor padrão para timeout (30 segundos)."


class TempoLimiteMiddleware(BaseHTTPMiddleware):
    """
    Limita o tempo total de processamento de uma sequência solicitação-resposta
    a `request_timeout` segundos. A intenção é prevenir ataques do tipo slow-loris.

    Caso o tempo limite seja excedido, gera um TempoLimiteExcedidoExcecao.
    """

    request_timeout: int

    def __init__(self, app, request_timeout: int = REQUEST_TIMEOUT):
        super().__init__(app)
        self.request_timeout = request_timeout

    async def dispatch(self, request: Request, call_next):
        try:
            with anyio.fail_after(self.request_timeout):
                return await call_next(request)
        except TimeoutError:
            raise TempoLimiteExcedidoExcecao()
