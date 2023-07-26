from fastapi import Request

from src.modelos.excecao import APIExcecaoBase


async def requestHandler(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as ex:
        if isinstance(ex, APIExcecaoBase):
            return ex.response()

        raise ex
