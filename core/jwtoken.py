from datetime import datetime, timedelta

from jose import JWTError, jwt

from core.config import config


def geraTokenAtivaConta(idUsuario: str, email: str, duracao: timedelta) -> str:
    """Gera e retorna um token JWT que pode ser usado para confirmar um email."""
    afirmacoes = {"sub": idUsuario, "email": email, "exp": datetime.now() + duracao}

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
    idUsuario = token_info.get("sub")

    if not email or not idUsuario:
        return {"mensagem": "Token inválido.", "status": "400"}

    # Retorna o email
    return {"mensagem": {"idUsuario": idUsuario, "email": email}, "status": "200"}


def geraLink(email: str) -> str:
    '''
    Gera um link contendo o email do usuário, na forma de um token, (com 
    prazo de validade) para a troca de senha.

    Retorna o link na forma str.
    '''
    # Data de validade do token
    validade = datetime.utcnow() + timedelta(minutes=15)
    # Gera o token
    token_info = {"email": email, "exp": validade}
    token = jwt.encode(token_info, config.SEGREDO_JWT, algorithm="HS256")

    # Gera o link para a troca de senha
    url = config.CAMINHO_BASE + "usuarios/troca-senha/?token=" + token
    return url


def processaTokenTrocaSenha(token) -> dict:
    '''
    Verifica a validade do token e resgata o email nele contido.
    Falha, se o token for inválido (expirado ou corrompido).

    Retorna um dicionário contendo os campos "status" e "mensagem".
    - "status" == "200" se e somente se o token for válido.
    - "mensagem" contém o email do usuário, ou uma mensagem de 
    erro caso o token não seja válido.
    '''
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
