import jwt

from datetime import datetime, timedelta

# Palavra chave para assinar o token
SECRET_KEY = "P#%w5R9h@#6eG&i@"
# Tempo de validade para o token de troca de senha
TOKEN_VALIDADE = timedelta(minutes=15)


# Gera um link para trocar a senha do usuário com o email fornecido
def geraLink(email: str, url_base: str):
    # Data de validade do token
    validade = datetime.utcnow() + TOKEN_VALIDADE
    # Gera o token
    token_info = {"email": email, "validade": validade.timestamp()}
    token = jwt.encode(token_info, SECRET_KEY)

    # Gera o link para a troca de senha
    url = url_base + "/troca-senha/" + token
    return url
