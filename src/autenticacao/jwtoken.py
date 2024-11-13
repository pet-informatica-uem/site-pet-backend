"""
Contém funções para geração e processamento de tokens JWT.
"""

import logging
from datetime import UTC, datetime, timedelta

from jose import JWTError, jwt

from src.config import config
from src.modelos.excecao import TokenInvalidoExcecao


def geraTokenAtivaConta(idUsuario: str, email: str, duracao: timedelta) -> str:
    """
    Gera um token JWT para ativação da conta do usuário com id `idUsuario`, email `email`, e duração `duracao`.

    :param idUsuario: ID do usuário.
    :param email: Email do usuário.
    :param duracao: Duração do token.

    :return token: Token JWT gerado.
    """
    afirmacoes = {"sub": idUsuario, "email": email, "exp": datetime.now() + duracao}

    token = jwt.encode(afirmacoes, config.SEGREDO_JWT, algorithm="HS256")
    return token


def processaTokenAtivaConta(token: str) -> dict[str, str]:
    """
    Verifica a validade do token e retorna o email e id de usuário nele contidos.
    Falha, se o token for inválido (expirado ou corrompido).

    :param token: Token JWT a ser processado.
    :return tokenData: Dicionário contendo os campos "idUsuario" e "email", onde "idUsuario" é o id do usuário e "email" é o email do usuário.
    :raises TokenInvalidoExcecao: Se o token for inválido.
    """
    # Tenta decodificar o token
    try:
        token_info: dict[str, str] = jwt.decode(
            token, config.SEGREDO_JWT, algorithms=["HS256"]
        )
    except JWTError as e:
        logging.warning(f"Token inválido, erro:\n {str(e)}")
        raise TokenInvalidoExcecao()

    # Recupera as informações do token
    email: str = token_info["email"]
    idUsuario: str = token_info["sub"]

    # Retorna o email
    return {"idUsuario": idUsuario, "email": email}


def geraLinkEsqueciSenha(email: str) -> str:
    """
    Gera um link contendo o email do usuário, na forma de um token, (com
    prazo de validade) para a troca de senha e o retorna.

    :param email: Email do usuário.
    :return url: Link contendo o token.
    """
    # Data de validade do token
    validade = datetime.utcnow() + timedelta(minutes=15)
    # Gera o token
    token_info = {"email": email, "validade": validade.timestamp()}
    token = jwt.encode(token_info, config.SEGREDO_JWT, algorithm="HS256")

    # Gera o link para a troca de senha
    # TODO ver com o front qual vai ser o link
    url = config.CAMINHO_BASE + "/esqueci-senha/?token=" + token
    return url


def processaTokenTrocaSenha(token: str) -> str:
    """
    Verifica a validade do token e resgata o email nele contido.
    Falha, se o token for inválido (expirado ou corrompido).

    :param token: Token JWT a ser processado.
    :return email: Email do usuário.
    :raises TokenInvalidoExcecao: Se o token for inválido.
    """
    # Tenta decodificar o token
    try:
        token_info = jwt.decode(token, config.SEGREDO_JWT, algorithms=["HS256"])
    except JWTError as e:
        logging.warning(f"Token inválido, erro:\n {str(e)}")
        raise TokenInvalidoExcecao()

    # Recupera as informações do token
    email: str = token_info["email"]
    validade = token_info["validade"]

    # Verifica a validade do token
    validade: datetime = datetime.fromtimestamp(validade)  # type: ignore
    if validade < datetime.now(UTC):
        raise TokenInvalidoExcecao()

    # Retorna o email
    return email
