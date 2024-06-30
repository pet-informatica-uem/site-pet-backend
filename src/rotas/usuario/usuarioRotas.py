import logging
from datetime import UTC, datetime
from typing import Annotated

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    Form,
    HTTPException,
    Request,
    UploadFile,
    status,
)
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, SecretStr

from src.config import config
from src.limiter import limiter
from src.modelos.bd import RegistroLoginBD, TokenAutenticacaoBD
from src.modelos.excecao import (
    APIExcecaoBase,
    ErroValidacaoExcecao,
    JaExisteExcecao,
    NaoAutenticadoExcecao,
    NaoAutorizadoExcecao,
    UsuarioNaoEncontradoExcecao,
    listaRespostasExcecoes,
)
from src.modelos.registro.registroLogin import RegistroLogin
from src.modelos.usuario.usuario import Petiano, TipoConta, Usuario
from src.modelos.usuario.usuarioClad import (
    UsuarioAtualizar,
    UsuarioAtualizarEmail,
    UsuarioAtualizarSenha,
    UsuarioCriar,
    UsuarioLer,
    UsuarioLerAdmin,
)
from src.modelos.usuario.validacaoCadastro import ValidacaoCadastro
from src.rotas.usuario.usuarioControlador import UsuarioControlador


class Token(BaseModel):
    access_token: str
    token_type: str


roteador: APIRouter = APIRouter(
    prefix="/usuarios",
    tags=["Usuário"],
)


tokenAcesso: OAuth2PasswordBearer = OAuth2PasswordBearer(
    tokenUrl=config.ROOT_PATH + "/usuarios/login"
)


def getUsuarioAutenticado(token: Annotated[str, Depends(tokenAcesso)]):
    try:
        return UsuarioControlador.getUsuarioAutenticado(token)
    except NaoAutenticadoExcecao:
        # esse HTTPException é necessário devido ao header incluso.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não autenticado",
            headers={"WWW-Authenticate": "Bearer"},
        )


def getPetianoAutenticado(usuario: Annotated[Usuario, Depends(getUsuarioAutenticado)]):
    if usuario.tipoConta == TipoConta.PETIANO:
        return usuario
    raise NaoAutorizadoExcecao()


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
@limiter.limit("3/minute")
def cadastrarUsuario(
    tasks: BackgroundTasks, request: Request, usuario: UsuarioCriar
) -> str:
    # despacha para controlador
    usuarioCadastrado = UsuarioControlador.cadastrarUsuario(usuario, tasks)

    # retorna os dados do usuario cadastrado
    return usuarioCadastrado


@roteador.get(
    "/",
    name="Recuperar usuários cadastrados",
    description="Rota apenas para petianos.\n\n" "Lista todos os usuários cadastrados.",
    response_model=list[UsuarioLerAdmin],
)
def listarUsuarios(
    usuario: Annotated[Usuario, Depends(getPetianoAutenticado)],
):
    return UsuarioControlador.getUsuarios()


@roteador.get(
    "/petiano",
    name="Recuperar petianos cadastrados",
    description="Lista todos os petianos cadastrados.",
    response_model=list[Petiano],
)
def listarPetianos():
    return UsuarioControlador.getPetianos()


@roteador.get(
    "/confirma-email",
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
def confirmaEmail(token: str):
    UsuarioControlador.ativarConta(token)


@roteador.get(
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


@roteador.post(
    "/esqueci-senha",
    name="Recuperar conta",
    description="""Envia um email para a conta fornecida para trocar a senha.
    Falha, caso o email da conta seja inválido.
    """,
)
@limiter.limit("3/minute")
def recuperaConta(
    tasks: BackgroundTasks, request: Request, email: Annotated[EmailStr, Form()]
):
    # Verifica se o email é válido
    if not ValidacaoCadastro.email(email):
        raise ErroValidacaoExcecao(message="Email inválido.")

    # Passa o email para o controlador
    UsuarioControlador.recuperarConta(email, tasks)


@roteador.post(
    "/altera-senha",
    name="Trocar senha",
    description="""
        Altera a senha do usuário. Falha, se a senha ou o link forem inválidos.
    """,
    status_code=status.HTTP_200_OK,
    responses=listaRespostasExcecoes(NaoAutenticadoExcecao),
)
def trocaSenha(tasks: BackgroundTasks, token: str, senha: Annotated[SecretStr, Form()]):
    # Validacao basica da senha
    if not ValidacaoCadastro.senha(senha.get_secret_value()):
        raise ErroValidacaoExcecao(message="Senha inválida.")

    # Despacha o token para o controlador
    UsuarioControlador.trocarSenha(token, senha.get_secret_value(), tasks)


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
@limiter.limit("3/minute")
def autenticar(
    request: Request, dados: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    # obtém dados
    email: str = dados.username
    senha: str = dados.password

    # normaliza email
    email: str = email.lower().strip()

    # chama controlador
    try:
        token = UsuarioControlador.autenticarUsuario(email, senha)

        reg: RegistroLogin = RegistroLogin(
            emailUsuario=email,
            ipUsuario=request.client.host,
            dataHora=datetime.now(UTC),
            sucesso=True,
        )
        RegistroLoginBD.criar(reg)

        return token
    except Exception as e:
        reg: RegistroLogin = RegistroLogin(
            emailUsuario=email,
            ipUsuario=request.client.host,
            dataHora=datetime.now(UTC),
            sucesso=False,
            motivo=str(e),
        )
        RegistroLoginBD.criar(reg)

        raise e


@roteador.delete(
    "/login",
    name="Desautenticar",
    description="""
    Desautentica o token fornecido.

    Caso o parâmetro todos seja fornecido, todas as sessões ativas do usuário serão deslogadas.
    """,
    status_code=status.HTTP_200_OK,
    responses=listaRespostasExcecoes(NaoAutenticadoExcecao),
)
def desautenticar(
    token: Annotated[str, Depends(tokenAcesso)], todos: bool | None = False
):
    usuario = getUsuarioAutenticado(token)
    if todos:
        TokenAutenticacaoBD.deletarTokensUsuario(usuario.id)
    else:
        TokenAutenticacaoBD.deletar(token)


@roteador.put(
    "/{id}/email",
    name="Editar email do usuário autenticado",
    description="""O usuário é capaz de editar seu email""",
)
def editarEmail(
    tasks: BackgroundTasks,
    id: str,
    dadosEmail: UsuarioAtualizarEmail,
    usuario: Annotated[Usuario, Depends(getUsuarioAutenticado)] = ...,  # type: ignore
):
    if usuario.id == id or usuario.tipoConta == TipoConta.PETIANO:
        if not ValidacaoCadastro.email(dadosEmail.novoEmail):
            raise ErroValidacaoExcecao(message="Email inválido.")
        # normaliza dados
        novoEmail = dadosEmail.novoEmail.lower().strip()
        dadosEmail.novoEmail = novoEmail

        UsuarioControlador.editarEmail(dadosEmail, id, tasks)

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
    tasks: BackgroundTasks,
    id: str,
    dadosSenha: UsuarioAtualizarSenha,
    deslogarAoTrocarSenha: bool,
    usuario: Annotated[Usuario, Depends(getUsuarioAutenticado)] = ...,  # type: ignore
):
    if usuario.id == id:
        # efetua troca de senha
        UsuarioControlador.editaSenha(
            dadosSenha,
            usuario,
            tasks,
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
    usuario: Annotated[Usuario, Depends(getPetianoAutenticado)] = ...,  # type: ignore
) -> None:
    if usuario.id == id:
        UsuarioControlador.editarFoto(usuario=usuario, foto=foto)


@roteador.post(
    "/{id}/petiano",
    name="Promover usuário a petiano",
    description="Promove o usuário especificado a petiano.",
)
def promoverPetiano(
    id: str, _usuario: Annotated[Usuario, Depends(getPetianoAutenticado)] = ...
):
    UsuarioControlador.promoverPetiano(id)


@roteador.delete(
    "/{id}/petiano",
    name="Rebaixar usuário a não petiano",
    description="""Remove o status de petiano do usuário especificado.
        Por padrão, a conta passa a ser do tipo egresso, mas caso o parâmetro egresso seja falso, o usuário é rebaixado a estudante.""",
)
def demitirPetiano(
    id: str,
    egresso: bool | None = True,
    _usuario: Annotated[Usuario, Depends(getPetianoAutenticado)] = ...,
):
    UsuarioControlador.demitirPetiano(id, egresso if egresso is not None else True)


@roteador.get(
    "/{id}",
    name="Obter detalhes do usuário com id fornecido",
    description="Retorna detalhes do usuário com id fornecido.\n\n"
    "Usuários não petianos só podem ver seus próprios dados.",
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
    name="Remove o usuário indicado",
    description="""
    Elimina o usuário.

    Usuários não petianos só podem excluir seus próprios perfis.
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


@roteador.get(
    "/{id}/historico-login",
    name="Histórico de login do usuário",
    description="""
    Retorna o histórico de login do usuário com o ID fornecido.

    Usuários não petianos só podem ver seu próprio histórico.
    """,
    status_code=status.HTTP_200_OK,
    response_model=list[RegistroLogin],
)
def getHistoricoLogin(
    usuario: Annotated[Usuario, Depends(getUsuarioAutenticado)], id: str
):
    if usuario.id != id and usuario.tipoConta != TipoConta.PETIANO:
        raise NaoAutorizadoExcecao()

    return UsuarioControlador.getHistoricoLogin(usuario.email)
