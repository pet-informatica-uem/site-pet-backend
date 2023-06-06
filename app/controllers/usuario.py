from app.models.usuarioBD import UsuarioBD

from datetime import datetime

import jwt

# Palavra chave para assinar o token
SECRET_KEY = "P#%w5R9h@#6eG&i@"


def trocaSenhaControlador(token) -> tuple:
    # Verifica o token e recupera o email
    retorno = processaTokenTrocaSenha(token)
    if retorno == "token_invalido" or email == "token_expirou":
        return (False, retorno)
    email = retorno

    # TODO atualizar a senha no bd
    return (True, "")


# Verifica a validade do token e retorno o email nele contido.
# Falha, se o token for inválido (expirado ou corrompido).
def processaTokenTrocaSenha(token) -> str:
    # Tenta decodificar o token
    try:
        token_info = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.exceptions.DecodeError:
        return "token_invalido"

    # Recupera as informações do token
    email = token_info.get("email")
    validade = token_info.get("validade")

    # Verifica a validade do token
    validade = datetime.fromtimestamp(validade)
    if validade > datetime.utcnow():
        return "token_expirou"

    # Retorna o email
    return email
