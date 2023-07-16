from fastapi import Request, status
from fastapi.responses import JSONResponse

from src.modelos.exceptions import APIExcecaoBase


async def request_handler(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as ex:
        if isinstance(ex, APIExcecaoBase):
            return ex.response()

        raise ex
