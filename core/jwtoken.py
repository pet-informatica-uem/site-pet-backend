from datetime import datetime, timedelta

from jose import JWTError, jwt

from core.config import config


def geraTokenAtivaConta(idUsuario: str, email: str, duracao: timedelta) -> str:
    """Gera e retorna um token JWT que pode ser usado para confirmar um email."""
    afirmacoes = {"id": idUsuario, "email": email, "exp": datetime.now() + duracao}

    token = jwt.encode(afirmacoes, config.SEGREDO_JWT, algorithm="HS256")
    return token


def processaTokenAtivaConta(token: str) -> dict:
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
        token_info = jwt.decode(token, config.SEGREDO_JWT, algorithms=["HS256"])
    except JWTError:
        return {"mensagem": "Token inválido.", "status": "400"}

    # Recupera as informações do token
    email = token_info.get("email")
    idUsuario = token_info.get("id")

    if not email or not idUsuario:
        return {"mensagem": "Token inválido.", "status": "400"}

    # Retorna o email
    return {"mensagem": {"idUsuario": idUsuario, "email": email}, "status": "200"}
