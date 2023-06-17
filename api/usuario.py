from app.controllers.usuario import recuperaContaControlador
from core import validaEmail

from pydantic import EmailStr
from typing import Annotated
from fastapi import APIRouter, Form, HTTPException, status, Request, Response


roteador = APIRouter(prefix="/usuarios", tags=["Usuários"])


@roteador.post(
    "/recupera",
    name="Recuperar conta",
    description="""
        Envia um email para a conta fornecida para trocar a senha.
        Falha, caso o email da conta seja inválido ou não esteja relacionado a uma conta cadastrada.
    """,
)
def recuperaConta(email: Annotated[EmailStr, Form()], request: Request, response: Response):
    email = EmailStr(email.lower())

    # Verifica se o email é válido
    if not validaEmail(email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email inválido.",
        )

    # Passa o email para o controlador
    resposta = recuperaContaControlador(email, str(request.base_url))

    response.status_code = int(resposta.get("status"))
    return {"mensagem": resposta.get("mensagem")}
