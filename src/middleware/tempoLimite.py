"""
Middleware que limita o tempo de recebimento da mensagem do usuário.
"""

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
    "Tempo limite de processamento da requisição. Após esse tempo, a exceção TempoLimiteExcedidoExcecao é gerada."

    def __init__(self, app, request_timeout: int = REQUEST_TIMEOUT):
        """
        Inicializa o middleware com o tempo limite de processamento da requisição.
        
        :param app: Aplicação FastAPI.
        :param request_timeout: Tempo limite de processamento da requisição.
        """
        super().__init__(app)
        self.request_timeout = request_timeout

    async def dispatch(self, request: Request, call_next):
        """
        Processa uma requisição, limitando o tempo de processamento a `request_timeout` segundos.

        Passa a requisição para o próximo middleware ou rota. Se o tempo limite for excedido,
        gera um TempoLimiteExcedidoExcecao.

        :param request: Requisição HTTP.
        :raises TempoLimiteExcedidoExcecao: Se o tempo limite for excedido.
        """
        try:
            with anyio.fail_after(self.request_timeout):
                return await call_next(request)
        except TimeoutError:
            raise TempoLimiteExcedidoExcecao()
