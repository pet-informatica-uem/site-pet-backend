from fastapi import Request

from src.modelos.excecao import APIExcecaoBase, TamanhoLimiteExcedidoExcecao
from content_size_limit_asgi.errors import ContentSizeExceeded

async def requestHandler(request: Request, call_next):
    # try:
         return await call_next(request)
    # except ContentSizeExceeded as ex:
    #    return TamanhoLimiteExcedidoExcecao().response()
    # except Exception as ex:
    #     print(ex)
    #     if isinstance(ex, APIExcecaoBase):
    #         return ex.response()

    #     raise ex
