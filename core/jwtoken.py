import jwt
from datetime import datetime, timedelta


# Palavra chave para assinar o token
SECRET_KEY = "P#%w5R9h@#6eG&i@"
# Tempo de validade para o token de troca de senha
TOKEN_VALIDADE = timedelta(minutes=15)


# Verifica a validade do token e retorno o email nele contido.
# Falha, se o token for inválido (expirado ou corrompido).
def processaTokenAtivaConta(token) -> dict:
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


# Gera um link para trocar a senha do usuário com o email fornecido
def geraLink(email: str, url_base: str):
    # Data de validade do token
    validade = datetime.utcnow() + TOKEN_VALIDADE
    # Gera o token
    token_info = {"email": email, "validade": validade.timestamp()}
    token = jwt.encode(token_info, SECRET_KEY)

    # Gera o link para a troca de senha
    url = url_base + "/usuarios/troca-senha/?token=" + token
    return url
