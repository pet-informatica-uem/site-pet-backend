from fastapi import HTTPException, Request
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from src.modelos.excecao import TamanhoLimiteExcedidoExcecao


class TamanhoLimiteMiddleware:
    """
    Limita o tamanho da mensagem recebida pelo usuário a `tamLimite` bytes.
    A intenção é prevenir ataques de negação de serviço por exaustão de memória.

    Caso o tamanho ultrapasse esse limite, o middleware gera uma HTTPException
    com o conteúdo de um TamahoLimiteExcedidoExcecao.
    """
    tamLimite: int | None

    def __init__(self, app: ASGIApp, *, size_limit: int | None = None) -> None:
        self.app = app
        self.tamLimite = size_limit

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http" or self.tamLimite is None:
            await self.app(scope, receive, send)
            return

        tamCorpo = 0

        async def receive_limiting() -> Message:
            nonlocal tamCorpo

            message = await receive()
            if message["type"] != "http.request":
                return message

            tamCorpo += len(message.get("body", b""))

            if tamCorpo > self.tamLimite:  # type: ignore
                # mágica: convertemos o TamanhoLimiteExcedidoExcecao em um HTTPException
                # porque? HTTPException é mágico e cancela o restante da solicitação
                # que coisa hein?
                exc = TamanhoLimiteExcedidoExcecao()
                raise HTTPException(status_code=exc.code, detail=exc.message)

            return message

        await self.app(scope, receive_limiting, send)
