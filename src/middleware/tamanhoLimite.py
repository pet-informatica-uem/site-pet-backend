from fastapi import HTTPException, Request

from starlette.types import ASGIApp, Message, Scope, Receive, Send

from src.modelos.excecao import TamanhoLimiteExcedidoExcecao


class TamanhoLimiteMiddleware:
    size_limit: int | None

    def __init__(self, app: ASGIApp, *, size_limit: int | None = None) -> None:
        self.app = app
        self.size_limit = size_limit

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http" or self.size_limit is None:
            await self.app(scope, receive, send)
            return

        body_size = 0

        async def receive_limiting() -> Message:
            nonlocal body_size

            message = await receive()
            if message["type"] != "http.request":
                return message

            body_size += len(message.get("body", b""))

            if body_size > self.size_limit:  # type: ignore
                # mágica: convertemos o TamanhoLimiteExcedidoExcecao em um HTTPException
                # porque? HTTPException é mágico e cancela o restante da solicitação
                # que coisa hein?
                exc = TamanhoLimiteExcedidoExcecao()
                raise HTTPException(status_code=exc.code, detail=exc.message)

            return message

        await self.app(scope, receive_limiting, send)
