from jose import jwt, JWTError
from datetime import datetime, timedelta

from core.config import config


# Gera um token que pode ser usado para confirmar um email
def geraTokenAtivaConta(idUsuario: str, email: str, duracao: timedelta) -> str:
    afirmacoes = {"id": idUsuario, "email": email, "exp": datetime.now() + duracao}

    token = jwt.encode(afirmacoes, config.SEGREDO_JWT, algorithm="HS256")
    return token


# Verifica a validade do token e retorno o email nele contido.
# Falha, se o token for inválido (expirado ou corrompido).
def processaTokenAtivaConta(token: str) -> dict:
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
    return {"idUsuario": idUsuario, "email": email, "status": "200"}
