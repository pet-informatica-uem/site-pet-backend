import asyncio

from fastapi import Request

from src.modelos.excecao import TempoLimiteExcedidoExcecao

REQUEST_TIMEOUT = 30


def TempoLimiteMiddleware(request_timeout=REQUEST_TIMEOUT):
    async def tempoLimiteMiddleware(request: Request, call_next):
        try:
            response = await asyncio.wait_for(
                call_next(request), timeout=request_timeout
            )
        except asyncio.TimeoutError:
            raise TempoLimiteExcedidoExcecao()
        return response

    return tempoLimiteMiddleware
