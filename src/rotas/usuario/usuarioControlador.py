import logging
import secrets
from datetime import datetime, timedelta
from bson import ObjectId

from fastapi import UploadFile
from pydantic import EmailStr, SecretStr
from src.modelos.autenticacao.autenticacaoClad import TokenAutenticacaoClad
from src.rotas.usuario.usuarioClad import (
    UsuarioAtualizar,
    UsuarioAtualizarEmail,
    UsuarioAtualizarSenha,
    UsuarioCriar,
)

from src.modelos.excecao import (
    APIExcecaoBase,
    ImagemInvalidaExcecao,
    NaoAutenticadoExcecao,
    NaoEncontradoExcecao,
    UsuarioJaExisteExcecao,
    UsuarioNaoEncontradoExcecao,
)
from src.autenticacao.autenticacao import conferirHashSenha, hashSenha
from src.autenticacao.jwtoken import (
    geraLink,
    geraTokenAtivaConta,
    processaTokenAtivaConta,
    processaTokenTrocaSenha,
)
from src.config import config
from src.email.operacoesEmail import resetarSenha, verificarEmail
from src.img.operacoesImagem import deletaImagem, validaImagem, armazenaFotoUsuario
from src.modelos.usuario.usuario import TipoConta, Usuario
from src.modelos.bd import colecaoUsuarios
from pymongo.errors import DuplicateKeyError


def ativaContaControlador(token: str) -> None:
    """
    Recebe um token JWT de ativação de conta.

    Caso o token seja válido, ativa a conta.
    """

    # Verifica o token e recupera o email
    msg: dict[str, str] = processaTokenAtivaConta(token)

    # Ativa a conta no BD
    assert msg is not None  # tipagem
    id: str = msg["idUsuario"]
    email: str = msg["email"]

    usuario = getUsuarioControlador(id)
    if usuario.email == email:
        usuario.emailConfirmado = True
        colecaoUsuarios.update_one(
            {"_id": ObjectId(id)}, usuario.model_dump()
        )


def cadastraUsuarioControlador(dadosUsuario: UsuarioCriar) -> Usuario:
    """
    Cria uma conta com os dados fornecidos, e envia um email
    de confirmação de criação de conta ao endereço fornecido.

        A criação da conta pode não suceder por erro na validação de dados,
        por já haver uma conta cadastrada com tal CPF ou email ou por falha
        de conexão com o banco de dados.
    """

    # normaliza dados
    dadosUsuario.email = dadosUsuario.email.lower().strip()
    dadosUsuario.cpf = "".join(c for c in dadosUsuario.cpf if c in "0123456789")
    dadosUsuario.nome = dadosUsuario.nome.strip()
    dadosUsuario.curso = dadosUsuario.curso.strip()

    # hash senha
    dadosUsuario.senha = hashSenha(dadosUsuario.senha.get_secret_value()) # type: ignore

    d = {
        "_id": secrets.token_hex(16),
        "emailConfirmado": False,
        "tipoConta": TipoConta.ESTUDANTE,
        "dataCriacao": datetime.now(),
    }

    d.update(dadosUsuario.model_dump())

    # cria instância de usuario
    usuario: Usuario = Usuario(**d)

    # cria usuario no bd
    try:
        id = colecaoUsuarios.insert_one(usuario.model_dump()).inserted_id
        usuario._id = str(id)
    except DuplicateKeyError:
        logging.error("Usuário já existe no banco de dados")
        raise UsuarioJaExisteExcecao()

    # gera token de ativação válido por 24h
    token: str = geraTokenAtivaConta(usuario._id, dadosUsuario.email, timedelta(days=1))

    # manda email de ativação
    # não é necessário fazer urlencode pois jwt é url-safe
    linkConfirmacao: str = (
        config.CAMINHO_BASE + "/usuario/confirmacaoEmail?token=" + token
    )
    # print(linkConfirmacao)
    verificarEmail(
        config.EMAIL_SMTP, config.SENHA_SMTP, dadosUsuario.email, linkConfirmacao
    )

    return getUsuarioControlador(id)


# Envia um email para trocar de senha se o email estiver cadastrado no bd
def recuperaContaControlador(email: str) -> None:
    # Verifica se o usuário está cadastrado no bd
    if not colecaoUsuarios.find_one({"email": email}):
        return

    # Gera o link e envia o email se o usuário estiver cadastrado
    link: str = geraLink(email)
    resetarSenha(config.EMAIL_SMTP, config.SENHA_SMTP, email, link)  # Envia o email


def trocaSenhaControlador(token, senha: str) -> None:
    # Verifica o token e recupera o email
    email: str = processaTokenTrocaSenha(token)

    usuario: Usuario = Usuario(**colecaoUsuarios.find_one({"email": email}))  # type: ignore

    usuario.senha = hashSenha(senha)

    colecaoUsuarios.update_one(
        {"_id": ObjectId(usuario._id)}, usuario.model_dump()
    )

    logging.info("Senha atualizada para o usuário com ID: " + str(usuario._id))


def autenticaUsuarioControlador(email: str, senha: str) -> dict:
    """
    Autentica e gera um token de autenticação para o usuário com email e senha
    indicados.
    """

    # verifica senha
    usuario: Usuario = Usuario(**colecaoUsuarios.find_one({"email": email}))  # type: ignore

    if not conferirHashSenha(senha, usuario.senha):
        raise NaoAutenticadoExcecao()

    # está ativo?
    if usuario.emailConfirmado != True:
        raise NaoAutenticadoExcecao()

    # cria token
    tk: str = secrets.token_urlsafe()
    TokenAutenticacaoClad.criar(
        tk,
        usuario._id,
        datetime.now() + timedelta(days=2),
    )

    # retorna token
    return {"access_token": tk, "token_type": "bearer"}


def getUsuarioAutenticadoControlador(token: str) -> Usuario:
    """
    Obtém dados do usuário dono do token fornecido. Falha se o token estiver expirado
    ou for inválido.
    """

    try:
        id: str = TokenAutenticacaoClad.get(token).idUsuario
    except NaoEncontradoExcecao:
        raise NaoAutenticadoExcecao()

    usuario: Usuario = Usuario(**colecaoUsuarios.find_one({"_id": ObjectId(id)}))  # type: ignore

    return usuario


def getUsuarioControlador(id: str) -> Usuario:
    """
    Obtém dados do usuário com o id fornecido.
    """

    if usuario := colecaoUsuarios.find_one({"_id": ObjectId(id)}):
        return Usuario(**usuario)

    raise UsuarioNaoEncontradoExcecao()


def getTodosUsuariosControlador() -> list[Usuario]:
    return [Usuario(**u) for u in colecaoUsuarios.find()]


def editaUsuarioControlador(
    id: str,
    dadosUsuario: UsuarioAtualizar,
) -> Usuario:
    """
    Atualiza os dados básicos (nome, curso, redes sociais, foto) da conta de um usuário existente.

    Este controlador assume que as redes sociais estejam no formato de links ou None.

    A atualização da conta pode não suceder por erro na validação de dados.
    """

    # obtém usuário
    usuario: Usuario = getUsuarioControlador(id)

    # verifica se o usuário é petiano
    if usuario.tipoConta != TipoConta.PETIANO:
        dadosUsuario.github = None
        dadosUsuario.linkedin = None
        dadosUsuario.instagram = None

    # normaliza dados
    if dadosUsuario.nome:
        dadosUsuario.nome = dadosUsuario.nome.strip()
    if dadosUsuario.curso:
        dadosUsuario.curso = dadosUsuario.curso.strip()

    # cria instância de usuario
    usuario = Usuario(
        **usuario.model_dump().update(dadosUsuario.model_dump(exclude_none=True))  # type: ignore
    )

    # altera o usuario no bd
    colecaoUsuarios.update_one(
        {"_id": ObjectId(usuario._id)}, {"$set": usuario.model_dump()}
    )

    return usuario


def deletaUsuarioControlador(id: str):
    getUsuarioControlador(id)

    colecaoUsuarios.delete_one({"_id": ObjectId(id)})


def editaSenhaControlador(dadosSenha: UsuarioAtualizarSenha, usuario: Usuario) -> None:
    """
    Atualiza a senha de um usuário existente caso a senha antiga seja correta.

    A atualização da conta pode não suceder por erro na validação de dados.
    """
    if conferirHashSenha(dadosSenha.senha.get_secret_value(), usuario.senha):
        usuario.senha = hashSenha(dadosSenha.novaSenha.get_secret_value())
        colecaoUsuarios.update_one(
            {"_id": ObjectId(usuario._id)}, {"$set": usuario.model_dump()}
        )
    else:
        raise APIExcecaoBase(mensagem="Senha incorreta")


def editaEmailControlador(dadosEmail: UsuarioAtualizarEmail, usuario: Usuario) -> None:
    """
    Atualiza o email de um usuário existente.

    Para atualizar o email, o usuário deve digitar sua senha atual.

    O usuário sempre é deslogado quando troca seu email, pois sua conta deve ser reativada.

    A atualização da conta pode não suceder por erro na validação de dados.
    """
    if conferirHashSenha(dadosEmail.senha.get_secret_value(), usuario.senha):
        usuario.email = dadosEmail.novoEmail
        colecaoUsuarios.update_one(
            {"_id": ObjectId(usuario._id)}, {"$set": usuario.model_dump()}
        )
    else:
        raise APIExcecaoBase(mensagem="Senha incorreta")


def editarFotoControlador(usuario: Usuario, foto: UploadFile) -> None:
    """
    Atualiza a foto de perfil de um usuário existente.

    Para atualizar a foto, o usuário deve inserir uma foto.

    A atualização da conta pode não suceder por erro na validação de dados.
    """
    if not validaImagem(foto.file):
        raise ImagemInvalidaExcecao()

    deletaImagem(usuario.nome, ["usuarios"])
    caminhoFotoPerfil: str = armazenaFotoUsuario(usuario.nome, foto.file)  # type: ignore
    usuario.foto = caminhoFotoPerfil  # type: ignore

    # atualiza no bd
    colecaoUsuarios.update_one(
        {"_id": ObjectId(usuario._id)}, {"$set": usuario.model_dump()}
    )
