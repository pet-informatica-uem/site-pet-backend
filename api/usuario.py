import logging
from typing import Annotated

from fastapi import APIRouter, Form, HTTPException, Request, Response, status
from pydantic import EmailStr, SecretStr

from app.controllers.usuario import (
    ativaContaControlador,
    cadastraUsuarioControlador,
    recuperaContaControlador,
)
from core.ValidacaoCadastro import validaCpf, validaEmail, validaSenha

roteador = APIRouter(
    prefix="/usuario",
    tags=["Usuário"],
)


@roteador.post(
    "/cadastrar",
    name="Cadastrar usuário",
    description="Cadastra um novo usuário com os dados fornecidos.\n"
    "Os dados fornecidos devem ser válidos. Os requisitos de senha são:\n"
    " - Deve possuir entre 8 e 64 caracteres\n"
    " - Deve ter ao menos uma letra maiúscula\n"
    " - Deve ter ao menos um dígito\n"
    " - Deve ter ao menos um caractere não alfanumérico\n",
    status_code=status.HTTP_201_CREATED,
)
async def cadastrarUsuario(
    nomeCompleto: Annotated[str, Form(max_length=200)],
    cpf: Annotated[str, Form(max_length=200)],
    email: Annotated[EmailStr, Form()],
    senha: Annotated[SecretStr, Form(max_length=200)],
    confirmacaoSenha: Annotated[SecretStr, Form(max_length=200)],
    curso: Annotated[str | None, Form(max_length=200)] = None,
):
    # valida dados
    if (
        not validaCpf(cpf)
        or not validaSenha(
            senha.get_secret_value(), confirmacaoSenha.get_secret_value()
        )
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
    resultado = cadastraUsuarioControlador(
        nomeCompleto, cpf, email, senha.get_secret_value(), curso
    )
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


@roteador.get(
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


@roteador.post(
    "/recupera",
    name="Recuperar conta",
    description="""
        Envia um email para a conta fornecida para trocar a senha.
        Falha, caso o email da conta seja inválido ou não esteja relacionado a uma conta cadastrada.
    """,
)
def recuperaConta(
    email: Annotated[EmailStr, Form()], request: Request, response: Response
):
    email = EmailStr(email.lower())

    # Verifica se o email é válido
    if not validaEmail(email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email inválido.",
        )

    # Passa o email para o controlador
    resposta = recuperaContaControlador(email)

    response.status_code = int(resposta["status"])
    return {"mensagem": resposta.get("mensagem")}
