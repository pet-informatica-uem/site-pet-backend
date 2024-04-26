import logging

from fastapi import Request

from src.modelos.excecao import APIExcecaoBase
from src.rotas.usuario.usuarioControlador import UsuarioControlador


async def requestLogging(request: Request, call_next):
    """
    Middleware para logar as requisições.
    """
    log_dict = {}
    response = await call_next(request)

    # tenta pegar o usuário autenticado
    idUsuario = None
    if request.headers.get("Authorization"):
        try:
            token = request.headers.get("Authorization").replace("Bearer ", "")  # type: ignore
            usuario = UsuarioControlador.getUsuarioAutenticado(token)  # type: ignore
            idUsuario = usuario.id
            print(log_dict)
        except Exception as e:
            pass

    log_dict.update(
        {
            "ip": request.client.host,  # type: ignore
            "usuario": idUsuario,
            "path": request.url.path,
            "method": request.method,
            "status_code": response.status_code,
        }
    )

    logging.info(log_dict, extra=log_dict)

    return response


async def requestHandler(request: Request, call_next):
    """
    Middleware para tratar exceções.
    """
    try:
        return await call_next(request)
    except Exception as ex:
        if isinstance(ex, APIExcecaoBase):
            return ex.response()

        raise ex
