import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from src.rotas.usuario.usuarioControlador import UsuarioControlador


class LoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
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