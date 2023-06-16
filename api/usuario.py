from datetime import datetime, timedelta
import logging
from typing import Annotated
from fastapi import APIRouter, Form, HTTPException, status
from pydantic import EmailStr
from app.controllers.operacoesEmail import verificarEmail
from app.controllers.usuario import ativaContaControlador, cadastraUsuarioControlador
from app.model.usuarioBD import UsuarioBD
from core import jwtoken
from core.config import config

from core.ValidacaoCadastro import validaCpf, validaEmail, validaSenha
from core.usuario import hashSenha

usuario = APIRouter(
    prefix="/usuario",
    tags=["Usuário"],
)


@usuario.post(
    "/cadastrar",
    name="Cadastrar usuário",
    description="Cadastra um novo usuário com os dados fornecidos. Os dados fornecidos devem ser válidos.",
    status_code=status.HTTP_201_CREATED,
)
async def cadastrarUsuario(
    nomeCompleto: Annotated[str, Form(max_length=200)],
    cpf: Annotated[str, Form(max_length=200)],
    email: Annotated[EmailStr, Form()],
    senha: Annotated[str, Form(max_length=200)],
    confirmacaoSenha: Annotated[str, Form(max_length=200)],
    curso: Annotated[str | None, Form(max_length=200)] = None,
):
    # valida dados
    if (
        not validaCpf(cpf)
        or not validaSenha(senha, confirmacaoSenha)
        or not validaEmail(email)
    ):
        logging.info(
            "Tentativa de cadastro de usuário com cpf, senha ou email inválido."
            + f" (CPF={cpf} Email={email})"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Dados inválidos"
        )

    # normaliza dados
    email = EmailStr(email.lower().strip())
    cpf = "".join(c for c in cpf if c in "0123456789")

    # despacha para controlador
    resultado = cadastraUsuarioControlador(nomeCompleto, cpf, email, senha, curso)
    if resultado["status"] != "201":
        logging.info(
            "Tentativa de cadastro de usuário falhou. Dados: "
            + str(resultado["mensagem"])
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Dados inválidos"
        )

    # retorna OK
    return resultado["mensagem"]


@usuario.get(
    "/confirmacaoEmail",
    name="Confirmação de email",
    description="Confirma o email de uma conta através do token suprido.",
    status_code=status.HTTP_200_OK,
)
async def confirmaEmail(token: str):
    resultado = ativaContaControlador(token)
    if resultado["status"] != "200":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Token inválido."
        )
