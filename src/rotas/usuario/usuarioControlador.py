import logging
import secrets
from datetime import datetime, timedelta

from fastapi import UploadFile
from modelos.excecao import ImagemInvalidaExcecao, NaoAutenticadoExcecao

from src.autenticacao.autenticacao import conferirHashSenha, hashSenha
from src.autenticacao.jwtoken import (
    geraLink,
    geraTokenAtivaConta,
    processaTokenAtivaConta,
    processaTokenTrocaSenha,
)
from src.config import config
from src.email.operacoesEmail import resetarSenha, verificarEmail
from src.img.operacoesImagem import deletaImagem
from src.modelos.autenticacao.autenticacaoTokenBD import AuthTokenBD
from src.modelos.usuario.usuario import EstadoConta, TipoConta, UsuarioSenha
from src.modelos.usuario.usuarioBD import UsuarioBD
from src.rotas.usuario.usuarioUtil import (
    ativaconta,
    atualizaSenha,
    verificaSeUsuarioExiste,
)


def ativaContaControlador(token: str) -> None:
    """
    Recebe um token JWT de ativação de conta.

    Caso o token seja válido, ativa a conta e retorna um dicionário
    com campo "status" igual a "200".

    Caso contrário, retorna um dicionário com campo "status" diferente
    de "200" e um campo "mensagem" contendo uma mensagem de erro.
    """

    # Verifica o token e recupera o email
    msg: dict[str, str] = processaTokenAtivaConta(token)

    # Ativa a conta no BD
    assert msg is not None  # tipagem
    id: str = msg["idUsuario"]
    email: str = msg["email"]

    ativaconta(id, email)


def cadastraUsuarioControlador(
    *, nomeCompleto: str, cpf: str, email: str, senha: str, curso: str | None
) -> str:
    """
    Cria uma conta com os dados fornecidos, e envia um email
    de confirmação de criação de conta ao endereço fornecido.

    Este controlador assume que o cpf e email já estão nas formas
    normalizadas (cpf contendo 11 dígitos, email sem espaço em branco
    prefixado ou sufixado e com todos os caracteres em caixa baixa).

    Retorna um dicionário contendo campos "status" e "mensagem".

    - Se a conta foi criada com sucesso, "status" == "201" e "mensagem" conterá
    o _id da conta (str).
    - Se a conta não foi criada com sucesso, "status" != "201" e "mensagem" conterá
    uma mensagem de erro (str).

    A criação da conta pode não suceder por erro na validação de dados,
    por já haver uma conta cadastrada com tal CPF ou email ou por falha
    de conexão com o banco de dados.
    """

    # 3. verifico se o email já existe e crio o usuário
    bd = UsuarioBD()
    id = bd.criarUsuario(
        {
            "nome": nomeCompleto,
            "email": email,
            "cpf": cpf,
            "curso": curso,
            "estado da conta": EstadoConta.INATIVO,
            "senha": hashSenha(senha),
            "tipo conta": TipoConta.ESTUDANTE,
            "data criacao": datetime.now(),
        }
    )

    # 4. gera token de ativação válido por 24h
    token = geraTokenAtivaConta(id, email, timedelta(days=1))

    # 5. manda email de ativação
    # não é necessário fazer urlencode pois jwt é url-safe
    linkConfirmacao = (
        config.CAMINHO_BASE + "/usuario/confirmacaoEmail?token=" + token
    )
    # print(linkConfirmacao)
    resultado = verificarEmail(
        config.EMAIL_SMTP, config.SENHA_SMTP, email, linkConfirmacao
    )

    return id


# Envia um email para trocar de senha se o email estiver cadastrado no bd
def recuperaContaControlador(email: str) -> None:
    # Verifica se o usuário está cadastrado no bd
    retorno = verificaSeUsuarioExiste(email)

    # Gera o link e envia o email se o usuário estiver cadastrado

    link = geraLink(email)
    resetarSenha(config.EMAIL_SMTP, config.SENHA_SMTP, email, link)  # Envia o email


def trocaSenhaControlador(token, senha: str) -> None:
    # Verifica o token e recupera o email
    email = processaTokenTrocaSenha(token)

    # Atualiza a senha no bd
    atualizaSenha(email, senha)

def autenticaUsuarioControlador(email: str, senha: str) -> dict:
    """
    Autentica e gera um token de autenticação para o usuário com email e senha
    indicados.

    Retorna um dicionário com campos "status" e "mensagem".

    - "status" == "200" se e somente se a autenticação ocorreu com sucesso.
    - "mensagem" contém um token de autenticação no formato OAuth2 se autenticado com
      sucesso, ou uma mensagem de erro caso contrário.
    """

    # verifica senha
    conexaoUsuario = UsuarioBD()

    id = conexaoUsuario.getIdUsuario(email)

    usuario = UsuarioSenha.deBd(conexaoUsuario.getUsuario(id))

    if not conferirHashSenha(senha, usuario.senha):
        raise NaoAutenticadoExcecao()

    # está ativo?
    if usuario.estadoConta != EstadoConta.ATIVO:
        raise NaoAutenticadoExcecao()

    # cria token
    tk = secrets.token_urlsafe()
    conexaoToken = AuthTokenBD()
    conexaoToken.criarToken(
        {
            "_id": tk,
            "idUsuario": usuario.id,
            "validade": datetime.now() + timedelta(days=2),
        }
    )

    # retorna token
    return {"access_token": tk, "token_type": "bearer"}


def getUsuarioAutenticadoControlador(token: str) -> UsuarioSenha:
    """
    Obtém dados do usuário dono do token fornecido. Falha se o token estiver expirado
    ou for inválido.

    Retorna um dicionário com campos "status" e "mensagem".
    - "status" == "200" se e somente se os dados foram recuperados com sucesso.
    - "mensagem" contém uma instância da classe UsuarioSenha em caso de sucesso e uma
      mensagem de erro caso contrário.
    """
    conexaoAuthToken = AuthTokenBD()

    id = conexaoAuthToken.getIdUsuarioDoToken(token)

    conexaoUsuario = UsuarioBD()

    usuario = UsuarioSenha.deBd(conexaoUsuario.getUsuario(id))
    return usuario


def getUsuarioControlador(id: str) -> UsuarioSenha:
    """
    Obtém dados do usuário com o id fornecido.

    Retorna um dicionário com campos "status" e "mensagem".

    - "status" == "200" se e somente se os dados foram recuperados com sucesso.
    - "mensagem" contém uma instância da classe UsuarioSenha em caso de sucesso e uma
      mensagem de erro caso contrário.
    """
    conexaoUsuario = UsuarioBD()
    return UsuarioSenha.deBd(conexaoUsuario.getUsuario(id))



def editaUsuarioControlador(
    *, usuario: UsuarioSenha, nomeCompleto: str, curso: str | None, redesSociais: dict
) -> None:
    """
    Atualiza os dados básicos (nome, curso, redes sociais) da conta de um usuário existente.

    Este controlador assume que as redes sociais estejam no formato de links ou None.

    Retorna um dicionário contendo campos "status" e "mensagem".

    - Se a conta foi atualizada, "status" == "200" e "mensagem" conterá
    o _id da conta (str).
    - Se a conta não foi atualizada com sucesso, "status" != "200" e "mensagem" conterá
    uma mensagem de erro (str).

    A atualização da conta pode não suceder por erro na validação de dados.
    """
    bd = UsuarioBD()
    usuarioDados: dict = usuario.paraBd()

    usuarioDados.update(
        {
            "nome": nomeCompleto,
            "curso": curso,
            "redes sociais": redesSociais,
        }
    )

    id = usuarioDados.pop("_id")
    bd.atualizarUsuario(id, usuarioDados)


def editaSenhaControlador(
    *, senhaAtual: str, novaSenha: str, usuario: UsuarioSenha
) -> None:
    """
    Atualiza a senha de um usuário existente.

    Para atualizar a senha, o usuário deve digitar sua senha atual.

    Retorna um dicionário contendo campos "status" e "mensagem".

    - Se a senha foi atualizada, "status" == "200" e "mensagem" conterá
    o _id da conta (str).
    - Se a senha não foi atualizada com sucesso, "status" != "200" e "mensagem" conterá
    uma mensagem de erro (str).

    A atualização da conta pode não suceder por erro na validação de dados.
    """
    bd = UsuarioBD()
    usuarioDados: dict = usuario.paraBd()
    if conferirHashSenha(senhaAtual, usuarioDados["senha"]):
        usuarioDados.update({"senha": hashSenha(novaSenha)})
        id = usuarioDados.pop("_id")
        bd.atualizarUsuario(id, usuarioDados)
    else:
        raise NaoAutenticadoExcecao()


def editaEmailControlador(
    *, senhaAtual: str, novoEmail: str, usuario: UsuarioSenha
) -> None:
    """
    Atualiza o email de um usuário existente.

    Para atualizar o email, o usuário deve digitar sua senha atual.

    O usuário sempre é deslogado quando troca seu email, pois sua conta deve ser reativada.

    Retorna um dicionário contendo campos "status" e "mensagem".

    - Se o email foi atualizado, "status" == "200" e "mensagem" conterá
    o _id da conta (str).
    - Se o email não foi atualizado com sucesso, "status" != "200" e "mensagem" conterá
    uma mensagem de erro (str).

    A atualização da conta pode não suceder por erro na validação de dados.
    """
    bd = UsuarioBD()
    usuarioDados: dict = usuario.paraBd()
    if conferirHashSenha(senhaAtual, usuarioDados["senha"]):
        usuarioDados.update({"email": novoEmail, "estado da conta": "inativo"})
        id = usuarioDados.pop("_id")
        bd.atualizarUsuario(id, usuarioDados)
        token24h = geraTokenAtivaConta(id, novoEmail, timedelta(days=1))
        linkConfirmacao = (
            config.CAMINHO_BASE + "/usuario/confirmacaoEmail?token=" + token24h
        )
        verificarEmail(
            emailPet=config.EMAIL_SMTP,
            senhaPet=config.SENHA_SMTP,
            emailDestino=novoEmail,
            link=linkConfirmacao,
        )
        logging.info("Dados do usuário atualizados, id: " + str(id))
    else:
        raise NaoAutenticadoExcecao()


def editarFotoControlador(
    *, usuario: UsuarioSenha, foto: UploadFile | None
) -> None:
    """
    Atualiza a foto de perfil de um usuário existente.

    Para atualizar a foto, o usuário deve inserir uma foto.

    Retorna um dicionário contendo campos "status" e "mensagem".

    - Se a foto for atualizada, "status" == "200" e "mensagem" conterá
    o _id da conta (str).
    - Se a foto não for atualizado com sucesso, "status" != "200" e "mensagem" conterá
    uma mensagem de erro (str).

    A atualização da conta pode não suceder por erro na validação de dados.
    """
    bd = UsuarioBD()
    usuarioDados: dict = usuario.paraBd()

    if not validaImagem(foto.file):  # type: ignore
        raise ImagemInvalidaExcecao()

    deletaImagem(usuarioDados["nome"], ["usuarios"])
    caminhoFotoPerfil = armazenaFotoUsuario(usuarioDados["nome"], foto.file)  # type: ignore
    usuarioDados["foto perfil"] = caminhoFotoPerfil
    id = usuarioDados.pop("_id")
    bd.atualizarUsuario(id, usuarioDados)
