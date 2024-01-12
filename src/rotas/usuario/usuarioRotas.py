import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile, status, requests, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, SecretStr

from src.modelos.bd import TokenAutenticacaoBD
from src.modelos.excecao import (
    APIExcecaoBase,
    JaExisteExcecao,
    NaoAutenticadoExcecao,
    NaoAutorizadoExcecao,
    UsuarioNaoEncontradoExcecao,
    listaRespostasExcecoes,
)
from src.modelos.usuario.usuario import TipoConta, Usuario
from src.modelos.usuario.usuarioClad import (
    UsuarioAtualizar,
    UsuarioAtualizarEmail,
    UsuarioAtualizarSenha,
    UsuarioCriar,
    UsuarioLer,
)
from src.modelos.usuario.validacaoCadastro import ValidacaoCadastro
from src.rotas.usuario.usuarioControlador import UsuarioControlador

from src.config import config


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
        return UsuarioControlador.getUsuarioAutenticado(token)
    except NaoAutenticadoExcecao:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não autenticado",
            headers={"WWW-Authenticate": "Bearer"},
        )


def getPetianoAutenticado(usuario: Annotated[Usuario, Depends(getUsuarioAutenticado)]):
    if usuario.tipoConta == "petiano":
        return usuario
    raise HTTPException(status_code=401, detail="Acesso negado.")

def getBD(parametro :str) -> str | type(...):
    if parametro == 'TESTE_BD':
        return config.NOME_BD_TESTE
    else:
        return ...


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
    responses=listaRespostasExcecoes(JaExisteExcecao, APIExcecaoBase),
)
def cadastrarUsuario(usuario: UsuarioCriar) -> str:
    # despacha para controlador
    usuarioCadastrado :str = UsuarioControlador.cadastrarUsuario(usuario)

    # retorna os dados do usuario cadastrado
    return usuarioCadastrado


@roteador.get(
    "/",
    name="Recuperar usuários cadastrados",
    description="Rota apenas para petianos.\n\n" "Lista todos os usuários cadastrados.",
    response_model=list[Usuario],
)
def listarUsuarios(
    usuario: Annotated[Usuario, Depends(getPetianoAutenticado)],
):
    return UsuarioControlador.getUsuarios()


@roteador.get(
    "/petianos",
    name="Recuperar petianos cadastrados",
    description="Lista todos os petianos cadastrados.",
    response_model=list[UsuarioLer],
)
def listarPetianos():
    return UsuarioControlador.getUsuarios(petiano=True)


@roteador.get(
<<<<<<< HEAD
    "/eu",
    name="Obter detalhes do usuário autenticado",
    description="""
    Retorna detalhes do usuário autenticado.
    """,
    status_code=status.HTTP_200_OK,
    response_model=UsuarioLerAdmin,
    responses=listaRespostasExcecoes(UsuarioNaoEncontradoExcecao),
)
def getEu(usuario: Annotated[Usuario, Depends(getUsuarioAutenticado)]):
    return usuario


@roteador.get(
    "/{id}",
    name="Obter detalhes do usuário com id fornecido",
    description="""
    Retorna detalhes do usuário com id fornecido.
    """,
    status_code=status.HTTP_200_OK,
    response_model=UsuarioLerAdmin,
    responses=listaRespostasExcecoes(UsuarioNaoEncontradoExcecao),
)
def getUsuario(usuario: Annotated[Usuario, Depends(getUsuarioAutenticado)], id: str):
    if usuario.id == id:
        return usuario
    elif usuario.tipoConta == TipoConta.PETIANO:
        vitima: Usuario = UsuarioControlador.getUsuario(id)
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
    if usuario.id == id or usuario.tipoConta == TipoConta.PETIANO:
        return UsuarioControlador.editarUsuario(id, dados)
    else:
        raise NaoAutorizadoExcecao()


@roteador.put(
    "/{id}/email",
    name="Editar email do usuário autenticado",
    description="""O usuário é capaz de editar seu email""",
)
def editarEmail(
    id: str,
    dadosEmail: UsuarioAtualizarEmail,
    usuario: Annotated[Usuario, Depends(getUsuarioAutenticado)] = ...,
):
    if usuario.id == id or usuario.tipoConta == TipoConta.PETIANO:
        if not ValidacaoCadastro.email(dadosEmail.novoEmail):
            logging.info("Erro. Novo email não foi validado com sucesso.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Dados inválidos"
            )
        # normaliza dados
        novoEmail = dadosEmail.novoEmail.lower().strip()
        dadosEmail.novoEmail = novoEmail

        UsuarioControlador.editarEmail(dadosEmail, id)

        TokenAutenticacaoBD.deletarTokensUsuario(usuario.id)
    else:
        raise NaoAutenticadoExcecao()


@roteador.put(
    "/{id}/senha",
    name="Editar senha do usuário autenticado",
    description="""O usuário é capaz de editar sua senha. Caso a opção deslogarAoTrocarSenha for ativada, todos as sessões serão deslogadas ao trocar a senha.""",
)
def editarSenha(
    id: str,
    dadosSenha: UsuarioAtualizarSenha,
    deslogarAoTrocarSenha: bool,
    usuario: Annotated[Usuario, Depends(getUsuarioAutenticado)] = ...,
):
    if usuario.id == id:
        # efetua troca de senha
        UsuarioControlador.editaSenha(
            dadosSenha,
            usuario,
        )

        # efetua logout de todas as sessões, caso o usuário desejar
        if deslogarAoTrocarSenha:
            TokenAutenticacaoBD.deletarTokensUsuario(usuario.id)


@roteador.put(
    "/{id}/foto",
    name="Atualizar foto de perfil",
    description="O usuário petiano é capaz de editar sua foto de perfil",
)
def editarFoto(
    id: str,
    foto: UploadFile,
    usuario: Annotated[Usuario, Depends(getPetianoAutenticado)] = ...,
) -> None:
    if usuario.id == id:
        UsuarioControlador.editarFoto(usuario=usuario, foto=foto)


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
    if usuario.id == id or usuario.tipoConta == TipoConta.PETIANO:
        UsuarioControlador.deletarUsuario(id)
    else:
        raise NaoAutorizadoExcecao()


@roteador.post(
    "/confirmar-email",
=======
    "/confirma-email",
>>>>>>> main
    name="Confirmação de email",
    description="Confirma o email de uma conta através do token suprido.",
    status_code=status.HTTP_200_OK,
    responses=listaRespostasExcecoes(
        NaoAutenticadoExcecao,
        UsuarioNaoEncontradoExcecao,
        APIExcecaoBase,
        JaExisteExcecao,
    ),
)
def confirmarEmail(token: str) -> str|None:
    id :str|None = UsuarioControlador.ativarConta(token)
    return id


@roteador.get(
    "/eu",
    name="Obter detalhes do usuário autenticado",
    description="""
    Retorna detalhes do usuário autenticado.
    """,
    status_code=status.HTTP_200_OK,
    response_model=Usuario,
    responses=listaRespostasExcecoes(UsuarioNaoEncontradoExcecao),
)
def getEu(usuario: Annotated[Usuario, Depends(getUsuarioAutenticado)]):
    return usuario


@roteador.post(
    "/esqueci-senha",
    name="Recuperar conta",
    description="""Envia um email para a conta fornecida para trocar a senha.
    Falha, caso o email da conta seja inválido ou não esteja relacionado a uma conta cadastrada.
    """,
    responses=listaRespostasExcecoes(UsuarioNaoEncontradoExcecao),
)
def recuperaConta(email: Annotated[EmailStr, Form()]):
    # Verifica se o email é válido
    if not ValidacaoCadastro.email(email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email inválido.",
        )

    # Passa o email para o controlador
    UsuarioControlador.recuperarConta(email)


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
    UsuarioControlador.trocarSenha(token, senha.get_secret_value())


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
    # obtém dados
    email: str = dados.username
    senha: str = dados.password

    # normaliza email
    email: str = email.lower().strip()

    # chama controlador
    return UsuarioControlador.autenticarUsuario(email, senha)


@roteador.put(
    "/{id}/email",
    name="Editar email do usuário autenticado",
    description="""O usuário é capaz de editar seu email""",
)
def editarEmail(
    id: str,
    dadosEmail: UsuarioAtualizarEmail,
    usuario: Annotated[Usuario, Depends(getUsuarioAutenticado)] = ...,
):
    if usuario.id == id or usuario.tipoConta == TipoConta.PETIANO:
        if not ValidacaoCadastro.email(dadosEmail.novoEmail):
            logging.info("Erro. Novo email não foi validado com sucesso.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Dados inválidos"
            )
        # normaliza dados
        novoEmail = dadosEmail.novoEmail.lower().strip()
        dadosEmail.novoEmail = novoEmail

        UsuarioControlador.editarEmail(dadosEmail, id)

        TokenAutenticacaoBD.deletarTokensUsuario(usuario.id)
    else:
        raise NaoAutenticadoExcecao()


@roteador.put(
    "/{id}/senha",
    name="Editar senha do usuário autenticado",
    description="""O usuário é capaz de editar sua senha. Caso a opção deslogarAoTrocarSenha 
    seja selecionada, todos as sessões serão deslogadas ao trocar a senha.""",
)
def editarSenha(
    id: str,
    dadosSenha: UsuarioAtualizarSenha,
    deslogarAoTrocarSenha: bool,
    usuario: Annotated[Usuario, Depends(getUsuarioAutenticado)] = ...,
):
    if usuario.id == id:
        # efetua troca de senha
        UsuarioControlador.editaSenha(
            dadosSenha,
            usuario,
        )

        # efetua logout de todas as sessões, caso o usuário desejar
        if deslogarAoTrocarSenha:
            TokenAutenticacaoBD.deletarTokensUsuario(usuario.id)


@roteador.put(
    "/{id}/foto",
    name="Atualizar foto de perfil",
    description="O usuário petiano é capaz de editar sua foto de perfil",
)
def editarFoto(
    id: str,
    foto: UploadFile,
    usuario: Annotated[Usuario, Depends(getPetianoAutenticado)] = ...,
) -> None:
    if usuario.id == id:
        UsuarioControlador.editarFoto(usuario=usuario, foto=foto)


@roteador.get(
    "/{id}",
    name="Obter detalhes do usuário com id fornecido",
    description="Retorna detalhes do usuário com id fornecido.\n\n"
    "Usuários não petianos só podem ver seus próprios dados.",
    status_code=status.HTTP_200_OK,
    response_model=Usuario,
    responses=listaRespostasExcecoes(UsuarioNaoEncontradoExcecao),
)
def getUsuario(usuario: Annotated[Usuario, Depends(getUsuarioAutenticado)], id: str):
    if usuario.id == id:
        return usuario
    elif usuario.tipoConta == TipoConta.PETIANO:
        vitima: Usuario = UsuarioControlador.getUsuario(id)
        return vitima
    else:
        raise NaoAutorizadoExcecao()


@roteador.patch(
    "/{id}",
    name="Editar dados do usuário selecionado",
    description="Edita os dados do usuário (exceto senha e email).\n\n"
    "Usuários não petianos só podem editar seus próprios dados.",
    status_code=status.HTTP_200_OK,
    response_model=UsuarioLer,
    responses=listaRespostasExcecoes(UsuarioNaoEncontradoExcecao),
)
def patchUsuario(
    usuario: Annotated[Usuario, Depends(getUsuarioAutenticado)],
    dados: UsuarioAtualizar,
    id: str,
):
    if usuario.id == id or usuario.tipoConta == TipoConta.PETIANO:
        return UsuarioControlador.editarUsuario(id, dados)
    else:
        raise NaoAutorizadoExcecao()


@roteador.delete(
    "/{id}",
    name="Remove o usuário indicado"
    "Usuários não petianos só podem excluir seus próprios perfis.",
    description="""
    Elimina o usuário.
    """,
)
def deletaUsuario(
    usuario: Annotated[Usuario, Depends(getUsuarioAutenticado)],
    id: str,
):
    if usuario.id == id or usuario.tipoConta == TipoConta.PETIANO:
        UsuarioControlador.deletarUsuario(id)
    else:
        raise NaoAutorizadoExcecao()
