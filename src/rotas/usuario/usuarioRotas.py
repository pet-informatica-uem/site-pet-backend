import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, SecretStr
from src.modelos.autenticacao.autenticacaoClad import TokenAutenticacaoClad
from src.modelos.usuario.usuario import TipoConta, Usuario
from src.modelos.usuario.validacaoCadastro import ValidacaoCadastro

from src.rotas.usuario.usuarioClad import (
    UsuarioAtualizar,
    UsuarioAtualizarEmail,
    UsuarioAtualizarSenha,
    UsuarioCriar,
    UsuarioLer,
)
from src.modelos.excecao import (
    APIExcecaoBase,
    NaoAutenticadoExcecao,
    NaoAutorizadoExcecao,
    UsuarioJaExisteExcecao,
    UsuarioNaoEncontradoExcecao,
    listaRespostasExcecoes,
)
from src.rotas.usuario.usuarioControlador import (
    ativaContaControlador,
    autenticaUsuarioControlador,
    cadastraUsuarioControlador,
    deletaUsuarioControlador,
    editaEmailControlador,
    editarFotoControlador,
    editaSenhaControlador,
    editaUsuarioControlador,
    getTodosUsuariosControlador,
    getUsuarioAutenticadoControlador,
    getUsuarioControlador,
    recuperaContaControlador,
    trocaSenhaControlador,
)


class Token(BaseModel):
    access_token: str
    token_type: str


roteador: APIRouter = APIRouter(
    prefix="/usuarios",
    tags=["Usuário"],
)


tokenAcesso: OAuth2PasswordBearer = OAuth2PasswordBearer(tokenUrl="/usuarios/login")


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
    usuario: Annotated[Usuario, Depends(getUsuarioAutenticado)]
):
    if usuario.tipoConta == "petiano":
        return usuario
    raise HTTPException(status_code=401, detail="Acesso negado.")


@roteador.post(
    "/",
    name="Cadastrar usuário",
    description="Cadastra um novo usuário com os dados fornecidos.\n"
    "Os dados fornecidos devem ser válidos. Os requisitos de senha são:\n"
    " - Deve possuir entre 8 e 64 caracteres\n"
    " - Deve ter ao menos uma letra maiúscula\n"
    " - Deve ter ao menos um dígito\n"
    " - Deve ter ao menos um caractere não alfanumérico\n",
    status_code=status.HTTP_201_CREATED,
    responses=listaRespostasExcecoes(UsuarioJaExisteExcecao, APIExcecaoBase),
    response_model=UsuarioLer,
)
def cadastrarUsuario(usuario: UsuarioCriar):
    # despacha para controlador
    usuarioCadastrado = cadastraUsuarioControlador(usuario)

    # retorna os dados do usuario cadastrado
    return usuarioCadastrado


@roteador.get(
    "/",
    name="Recuperar usuários cadastrados",
    description="Lista todos os usuários cadastrados.",
    response_model=list[Usuario],
)
def listarUsuarios(
    usuario: Annotated[Usuario, Depends(getPetianoAutenticado)],
):
    return getTodosUsuariosControlador()


@roteador.get(
    "/{id}",
    name="Obter detalhes do usuário com id fornecido",
    description="""
    Retorna detalhes do usuário com id fornecido.
    """,
    status_code=status.HTTP_200_OK,
    response_model=UsuarioLer,
    responses=listaRespostasExcecoes(UsuarioNaoEncontradoExcecao),
)
def getUsuario(usuario: Annotated[Usuario, Depends(getUsuarioAutenticado)], id: str):
    if usuario._id == id:
        return usuario
    elif usuario.tipoConta == TipoConta.PETIANO:
        vitima: Usuario = getUsuarioControlador(id)
        return vitima
    else:
        raise NaoAutorizadoExcecao()


@roteador.patch(
    "/{id}",
    name="Editar dados do usuário selecionado",
    description="""
    Edita os dados do usuário (exceto senha e email).
    """,
    status_code=status.HTTP_200_OK,
    response_model=UsuarioLer,
    responses=listaRespostasExcecoes(UsuarioNaoEncontradoExcecao),
)
def patchUsuario(
    usuario: Annotated[Usuario, Depends(getUsuarioAutenticado)],
    dados: UsuarioAtualizar,
    id: str,
):
    if usuario._id == id or usuario.tipoConta == TipoConta.PETIANO:
        return editaUsuarioControlador(id, dados)
    else:
        raise NaoAutorizadoExcecao()


@roteador.put(
    "/{id}/email",
    name="Editar email do usuário autenticado",
    description="""O usuário é capaz de editar seu email""",
)
def editarEmail(
    dadosEmail: UsuarioAtualizarEmail,
    usuario: Annotated[Usuario, Depends(getUsuarioAutenticado)] = ...,
):
    if not ValidacaoCadastro.email(dadosEmail.novoEmail):
        logging.info("Erro. Novo email não foi validado com sucesso.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Dados inválidos"
        )

    # normaliza dados
    novoEmail = EmailStr(dadosEmail.novoEmail.lower().strip())

    editaEmailControlador(dadosEmail, usuario)

    TokenAutenticacaoClad.deletarTokensUsuario(usuario._id)


@roteador.put(
    "/{id}/senha",
    name="Editar senha do usuário autenticado",
    description="""O usuário é capaz de editar sua senha. Caso a opção deslogarAoTrocarSenha for ativada, todos as sessões serão deslogadas ao trocar a senha.""",
)
def editarSenha(
    dadosSenha: UsuarioAtualizarSenha,
    deslogarAoTrocarSenha: Annotated[bool, Form()],
    usuario: Annotated[Usuario, Depends(getUsuarioAutenticado)] = ...,
):
    # efetua troca de senha
    editaSenhaControlador(
        dadosSenha,
        usuario,
    )

    # efetua logout de todas as sessões, caso o usuário desejar
    if deslogarAoTrocarSenha:
        TokenAutenticacaoClad.deletarTokensUsuario(usuario._id)



@roteador.put(
    "/{id}/foto",
    name="Atualizar foto de perfil",
    description="O usuário petiano é capaz de editar sua foto de perfil",
)
def editarFoto(
    foto: UploadFile,
    usuario: Annotated[Usuario, Depends(getPetianoAutenticado)] = ...,
) -> None:
    editarFotoControlador(usuario=usuario, foto=foto)


@roteador.delete(
    "/{id}",
    name="Remove o usuário indicado",
    description="""
    Elimina o usuário.
    """,
)
def deletaUsuario(
    usuario: Annotated[Usuario, Depends(getUsuarioAutenticado)],
    id: str,
):
    if usuario._id == id or usuario.tipoConta == TipoConta.PETIANO:
        deletaUsuarioControlador(id)
    else:
        raise NaoAutorizadoExcecao()


@roteador.post(
    "/confirma-email",
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
    "/esqueci-senha",
    name="Recuperar conta",
    description="""
        Envia um email para a conta fornecida para trocar a senha.
        Falha, caso o email da conta seja inválido ou não esteja relacionado a uma conta cadastrada.
    """,
    responses=listaRespostasExcecoes(UsuarioNaoEncontradoExcecao),
)
def recuperaConta(email: Annotated[EmailStr, Form()]):
    email = EmailStr(email.lower())

    # Verifica se o email é válido
    if not ValidacaoCadastro.email(email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email inválido.",
        )

    # Passa o email para o controlador
    recuperaContaControlador(email)


@roteador.post(
    "/altera-senha",
    name="Trocar senha",
    description="""
        Altera a senha do usuário. Falha, se a senha ou o link forem inválidos.
    """,
    status_code=status.HTTP_200_OK,
    responses=listaRespostasExcecoes(NaoAutenticadoExcecao),
)
def trocaSenha(token: str, senha: Annotated[SecretStr, Form()]):
    # Validacao basica da senha
    if not ValidacaoCadastro.senha(senha.get_secret_value()):
        raise HTTPException(status_code=400, detail="Senha inválida.")

    # Despacha o token para o controlador
    trocaSenhaControlador(token, senha.get_secret_value())


@roteador.post(
    "/login",
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
