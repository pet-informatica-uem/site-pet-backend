import logging
from typing import Annotated

from fastapi import (APIRouter, Depends, Form, HTTPException, Request,
                     Response, UploadFile, status)
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, HttpUrl, SecretStr

from src.modelos.excecao import (APIExcecaoBase, NaoAutenticadoExcecao,
                             NaoEncontradoExcecao, UsuarioJaExisteExcecao,
                             UsuarioNaoEncontradoExcecao,
                             listaRespostasExcecoes)
from src.modelos.autenticacao.autenticacaoTokenBD import AuthTokenBD
from src.modelos.usuario.usuario import Usuario, UsuarioSenha
from src.modelos.usuario.validacaoCadastro import (validaCpf, validaEmail,
                                                   validaSenha)
from src.rotas.usuario.usuarioControlador import (
    ativaContaControlador, autenticaUsuarioControlador,
    cadastraUsuarioControlador, editaEmailControlador, editarFotoControlador,
    editaSenhaControlador, editaUsuarioControlador,
    getUsuarioAutenticadoControlador, getUsuarioControlador,
    recuperaContaControlador, trocaSenhaControlador)


class Token(BaseModel):
    access_token: str
    token_type: str


roteador: APIRouter = APIRouter(
    prefix="/usuario",
    tags=["Usuário"],
)


tokenAcesso: OAuth2PasswordBearer = OAuth2PasswordBearer(tokenUrl="/usuario/token")


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
    responses=listaRespostasExcecoes(UsuarioJaExisteExcecao, APIExcecaoBase),
)
def cadastrarUsuario(
    nomeCompleto: Annotated[str, Form(max_length=200)],
    cpf: Annotated[str, Form(max_length=200)],
    email: Annotated[EmailStr, Form()],
    senha: Annotated[SecretStr, Form(max_length=200)],
    confirmacaoSenha: Annotated[SecretStr, Form(max_length=200)],
    curso: Annotated[str | None, Form(max_length=200)] = None,
) -> str:
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
    id: str = cadastraUsuarioControlador(
        nomeCompleto=nomeCompleto,
        cpf=cpf,
        email=email,
        senha=senha.get_secret_value(),
        curso=curso,
    )

    # retorna OK
    return id


@roteador.get(
    "/confirmacaoEmail",
    name="Confirmação de email",
    description="Confirma o email de uma conta através do token suprido.",
    status_code=status.HTTP_200_OK,
    responses=listaRespostasExcecoes(
        NaoAutenticadoExcecao,
        UsuarioNaoEncontradoExcecao,
        APIExcecaoBase,
        UsuarioJaExisteExcecao,
    ),
)
def confirmaEmail(token: str):
    ativaContaControlador(token)


@roteador.post(
    "/recupera",
    name="Recuperar conta",
    description="""
        Envia um email para a conta fornecida para trocar a senha.
        Falha, caso o email da conta seja inválido ou não esteja relacionado a uma conta cadastrada.
    """,
    responses=listaRespostasExcecoes(UsuarioNaoEncontradoExcecao),
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
    recuperaContaControlador(email)


@roteador.post(
    "/troca-senha",
    name="Trocar senha",
    description="""
        Altera a senha do usuário. Falha, se a senha ou o link forem inválidos.
    """,
    status_code=status.HTTP_200_OK,
    responses=listaRespostasExcecoes(NaoAutenticadoExcecao),
)
def trocaSenha(token, senha: Annotated[str, Form()]):
    # Validacao basica da senha
    if not validaSenha(senha, senha):
        raise HTTPException(status_code=400, detail="Senha inválida.")

    # Despacha o token para o controlador
    trocaSenhaControlador(token, senha)


@roteador.post(
    "/token",
    name="Autenticar",
    description="""
    Autentica o usuário através do email e senha fornecidos.
    """,
    status_code=status.HTTP_200_OK,
    response_model=Token,
    responses=listaRespostasExcecoes(NaoAutenticadoExcecao),
)
def autenticar(dados: Annotated[OAuth2PasswordRequestForm, Depends()]):
    exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não autenticado",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # obtém dados
    email: str = dados.username
    senha: str = dados.password

    # normaliza email
    email: str = email.lower().strip()

    # chama controlador
    return autenticaUsuarioControlador(email, senha)


def getUsuarioAutenticado(token: Annotated[str, Depends(tokenAcesso)]):
    try:
        return getUsuarioAutenticadoControlador(token)
    except NaoAutenticadoExcecao as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não autenticado",
            headers={"WWW-Authenticate": "Bearer"},
        )


def getPetianoAutenticado(
    usuario: Annotated[UsuarioSenha, Depends(getUsuarioAutenticado)]
):
    if usuario.tipoConta == "petiano":
        return usuario
    raise HTTPException(status_code=401, detail="Acesso negado.")


@roteador.get(
    "/id/eu",
    name="Obter detalhes do usuário autenticado",
    description="""
    Retorna detalhes do usuário autenticado.
    """,
    status_code=status.HTTP_200_OK,
    response_model=Usuario,
    responses=listaRespostasExcecoes(NaoEncontradoExcecao, UsuarioNaoEncontradoExcecao),
)
def getUsuarioEu(usuario: Annotated[UsuarioSenha, Depends(getUsuarioAutenticado)]):
    return usuario


@roteador.get(
    "/id/{id}",
    name="Obter detalhes do usuário autenticado",
    description="""
    Retorna detalhes do usuário autenticado.
    """,
    status_code=status.HTTP_200_OK,
    response_model=Usuario,
    responses=listaRespostasExcecoes(UsuarioNaoEncontradoExcecao),
)
def getUsuario(_token: Annotated[str, Depends(tokenAcesso)], id: str):
    return getUsuarioControlador(id)


@roteador.post(
    "/editar-foto",
    name="Atualizar foto de perfil",
    description="O usuário petiano é capaz de editar sua foto de perfil",
)
def editarFoto(
    foto: UploadFile | None,
    usuario: Annotated[UsuarioSenha, Depends(getPetianoAutenticado)] = ...,
) -> None:
    editarFotoControlador(usuario=usuario, foto=foto)


@roteador.post(
    "/editar-dados",
    name="Editar dados do usuário autenticado",
    description="""O usuário é capaz de editar os dados""",
)
def editarDados(
    nomeCompleto: Annotated[str, Form(max_length=200)],
    curso: Annotated[str, Form(max_length=200)],
    github: Annotated[HttpUrl | None, Form()] = None,
    instagram: Annotated[HttpUrl | None, Form()] = None,
    linkedin: Annotated[HttpUrl | None, Form()] = None,
    twitter: Annotated[HttpUrl | None, Form()] = None,
    usuario: Annotated[UsuarioSenha, Depends(getUsuarioAutenticado)] = ...,
):
    redesSociais = None
    # agrupa redes sociais
    if usuario.tipoConta == 'petiano':
        redesSociais: dict[str, str] = {
            "github": github,
            "linkedin": linkedin,
            "instagram": instagram,
            "twitter": twitter,
        }

        # valida links
        for chave in redesSociais:
            link = str(redesSociais[chave])
            if chave not in link:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="O link " + link + " não é válido com a rede social " + chave,
                )

    editaUsuarioControlador(
        usuario=usuario,
        nomeCompleto=nomeCompleto,
        curso=curso,
        redesSociais=redesSociais,
    )


@roteador.post(
    "/alterar-senha",
    name="Editar senha do usuário autenticado",
    description="""O usuário é capaz de editar sua senha\n
    Caso a opção deslogarAoTrocarSenha for ativada, todos as sessões serão deslogadas ao trocar a senha.""",
)
def editarSenha(
    senhaAtual: Annotated[SecretStr, Form(max_length=200)],
    novaSenha: Annotated[SecretStr, Form(max_length=200)],
    deslogarAoTrocarSenha: Annotated[bool, Form()],
    usuario: Annotated[UsuarioSenha, Depends(getUsuarioAutenticado)] = ...,
    token: Annotated[str, Depends(tokenAcesso)] = ...,
):
    # verifica nova senha
    if not validaSenha(
        novaSenha.get_secret_value(), novaSenha.get_secret_value()
    ):
        logging.info("Erro. Nova senha não foi validada com sucesso.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Dados inválidos"
        )

    # efetua troca de senha
    editaSenhaControlador(
        senhaAtual=senhaAtual.get_secret_value(),
        novaSenha=novaSenha.get_secret_value(),
        usuario=usuario,
    )

    # efetua logout de todas as sessões, caso o usuário desejar
    if deslogarAoTrocarSenha:
        gerenciarTokens: AuthTokenBD = AuthTokenBD()
        gerenciarTokens.deletarTokensUsuario(
            gerenciarTokens.getIdUsuarioDoToken(token=token)
        )


@roteador.post(
    "/alterar-email",
    name="Editar email do usuário autenticado",
    description="""O usuário é capaz de editar seu email""",
)
def editarEmail(
    senhaAtual: Annotated[SecretStr, Form(max_length=200)],
    novoEmail: Annotated[EmailStr, Form()],
    usuario: Annotated[UsuarioSenha, Depends(getUsuarioAutenticado)] = ...,
    token: Annotated[str, Depends(tokenAcesso)] = ...,
):
    if not validaEmail(novoEmail):
        logging.info("Erro. Novo email não foi validado com sucesso.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Dados inválidos"
        )

    # normaliza dados
    novoEmail = EmailStr(novoEmail.lower().strip())

    editaEmailControlador(
        senhaAtual=senhaAtual.get_secret_value(),
        novoEmail=novoEmail,
        usuario=usuario,
    )

    gerenciarTokens: AuthTokenBD = AuthTokenBD()
    gerenciarTokens.deletarTokensUsuario(
        gerenciarTokens.getIdUsuarioDoToken(token=token)
    )
