from datetime import datetime, timedelta
import logging

from jose import JWTError, jwt

from src.config import config
from src.modelos.excecao import TokenInvalidoExcecao


def geraTokenAtivaConta(idUsuario: str, email: str, duracao: timedelta) -> str:
    """Gera e retorna um token JWT que pode ser usado para confirmar um email."""
    afirmacoes = {"sub": idUsuario, "email": email, "exp": datetime.now() + duracao}

    token = jwt.encode(afirmacoes, config.SEGREDO_JWT, algorithm="HS256")
    return token


def processaTokenAtivaConta(token: str) -> dict[str, str]:
    """
    Verifica a validade do token e retorna o email e id de usuário nele contidos.
    Falha, se o token for inválido (expirado ou corrompido).

    Retorna um dicionário contendo campos "status" e "mensagem".
    - "status" == "200" se e somente se o token for válido.
    - "mensagem" é um dicionário contendo chaves "idUsuario" e "email"
      caso o token seja válido, ou uma mensagem de erro caso contrário.
    """
    # Tenta decodificar o token
    try:
        token_info: dict[str, str] = jwt.decode(
            token, config.SEGREDO_JWT, algorithms=["HS256"]
        )
    except JWTError as e:
        logging.warning(f"Token inválido, error messagem:\n {str(e)}")
        raise TokenInvalidoExcecao()

    # Recupera as informações do token
    email: str = token_info["email"]
    idUsuario: str = token_info["sub"]

    # Retorna o email
    return {"idUsuario": idUsuario, "email": email}


def geraLinkEsqueciSenha(email: str) -> str:
    """
    Gera um link contendo o email do usuário, na forma de um token, (com
    prazo de validade) para a troca de senha.

    Retorna o link na forma str.
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

    Retorna um dicionário contendo os campos "status" e "mensagem".
    - "status" == "200" se e somente se o token for válido.
    - "mensagem" contém o email do usuário, ou uma mensagem de
    erro caso o token não seja válido.
    """
    # Tenta decodificar o token
    try:
        token_info = jwt.decode(token, config.SEGREDO_JWT, algorithms=["HS256"])
    except JWTError:
        raise TokenInvalidoExcecao()

    # Recupera as informações do token
    email: str = token_info["email"]
    validade = token_info["validade"]

    # Verifica a validade do token
    validade: datetime = datetime.fromtimestamp(validade)  # type: ignore
    if validade < datetime.utcnow():
        raise TokenInvalidoExcecao()

    # Retorna o email
    return email
