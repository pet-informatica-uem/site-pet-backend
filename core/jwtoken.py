import jwt

from datetime import datetime


# Palavra chave para assinar o token
SECRET_KEY = "P#%w5R9h@#6eG&i@"


# Verifica a validade do token e retorno o email nele contido.
# Falha, se o token for inválido (expirado ou corrompido).
def processaTokenTrocaSenha(token) -> dict:
    # Tenta decodificar o token
    try:
        token_info = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.exceptions.DecodeError:
        return {"mensagem": "Token inválido.", "status": "400"}

    # Recupera as informações do token
    email = token_info.get("email")
    validade = token_info.get("validade")

    # Verifica a validade do token
    validade = datetime.fromtimestamp(validade)
    if validade > datetime.utcnow():
        return {"mensagem": "Token expirou.", "status": "400"}

    # Retorna o email
    return {"email": email, "status": "200"}
