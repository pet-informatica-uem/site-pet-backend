from fastapi import Request

from src.modelos.excecao import APIExcecaoBase


def ExcecaoAPIMiddleware(request: Request, call_next):
    try:
        return call_next(request)
    except APIExcecaoBase as exc:
        return exc.response()
