from app.schemas.usuario import CadastroUsuario
from app.models.usuario import Usuario, UsuarioBd
from app.controllers.usuario import recuperaContaControlador
from core import bd, ValidaSenha, ValidaEmail, ValidaCPF, enviarEmail

import logging
from pydantic import EmailStr
from typing import Annotated
from fastapi import APIRouter, Form, HTTPException, Response, status, Request
from bson import ObjectId

from core.autenticacao import hashSenha


roteador = APIRouter(prefix="/usuarios", tags=["Usuários"])


@roteador.get(
    "/detalhes/{id}",
    name="Detalhes do usuário",
    description="Obtém os detalhes detalhes do usuário.",
    response_model=Usuario,
)
def detalhesUsuario(id: str):
    # TODO autenticar primeiro
    with bd.criaConexao() as conexao:
        usuariosBd = conexao.get_database("backend")
        colecao = usuariosBd.get_collection("usuarios")
        resultado = colecao.find_one({"_id": ObjectId(id)})

        if resultado:
            return resultado
        else:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, detail="O usuário não existe"
            )


@roteador.post(
    "/cadastrar",
    name="Cadastrar Usuário",
    description="""
        Cadastra um usuário com as informações dadas e envia um email de confirmação.
        Falha, caso os dados não sejam válidos ou caso um usuário já exista com esse email cadastrado.
    """,
    status_code=status.HTTP_201_CREATED,
)
def cadastrarUsuario(
    email: Annotated[EmailStr, Form()],
    senha: Annotated[str, Form()],
    confirmacaoSenha: Annotated[str, Form()],
    nome: Annotated[str, Form()],
    cpf: Annotated[str, Form()],
    response: Response,
):
    dados = CadastroUsuario(
        email=EmailStr(email.lower()),  # lembrar de deixar o email em caixa baixa
        senha=senha,
        confirmacaoSenha=confirmacaoSenha,
        nome=nome,
        cpf=cpf,
    )

    # 1. validar dados recebidos
    if (
        not ValidaCPF(dados.cpf)
        or not ValidaEmail(dados.email)
        or not ValidaSenha(dados.senha, dados.confirmacaoSenha)
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Senha, email ou CPF informados inválidos.",
        )

    # 2. verificar se o usuário já existe (username, email)
    with bd.criaConexao() as conexao:
        backendBd = conexao.get_database("backend")
        colecao = backendBd.get_collection("usuarios")

        if colecao.find_one({"email": dados.email}):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

        # 3. criar entrada no BD
        usuarioObjeto = UsuarioBd(
            nome=dados.nome,
            cpf=dados.cpf,
            email=dados.email,
            senha=hashSenha(dados.senha),
            emailValidado=False,
        )

        resultado = colecao.insert_one(usuarioObjeto.dict())
        logging.info("Criado novo usuário com ID " + str(resultado.inserted_id))

        # 4. enviar email de confirmação
        enviarEmail()

        # log ok
        usuarioCensurado = usuarioObjeto.dict()
        usuarioCensurado.update({"senha": "[SENHA]"})
        logging.debug("Dados do usuã́rio criado: " + repr(usuarioCensurado))

        response.headers["Location"] = str(resultado.inserted_id)


@roteador.post(
    "/recupera",
    name="Recuperar conta",
    description="""
        Envia um email para a conta fornecida para trocar a senha.
        Falha, caso o email da conta seja inválido ou não esteja relacionado a uma conta cadastrada.
    """,
)
def recuperaConta(email: Annotated[EmailStr, Form()], request: Request):
    email = EmailStr(email.lower())

    # Verifica se o email é válido
    if not ValidaEmail(email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email inválido.",
        )
    
    #Passa o email para o controlador
    controlador = recuperaContaControlador(email, request.base_url())
