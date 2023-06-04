from app.models.usuarioBD import UsuarioBD
from core import enviarEmail

from datetime import datetime, timedelta

import logging
import jwt


# Palavra chave para assinar o token
SECRET_KEY = "P#%w5R9h@#6eG&i@"
# Tempo de validade para o token de troca de senha
TOKEN_VALIDADE = timedelta(minutes=15)


# Envia um email para trocar de senha se o email estiver cadastrado no bd
def recuperaContaControlador(email: str, url_base: str) -> tuple:
    try:
        conexao = UsuarioBD()

        # Verifica se existe usuário com esse email
        if conexao.getIdUsuario(email) == "Usuário não encontrado":
            return (False, "não existe")
    except Exception as e:
        logging.error("Erro no banco de dados: " + str(e))
        return (False, "interno")

    # Gera o link e envia o email
    link = geraLink(email, url_base)
    enviarEmail(link)
    return (True, "enviado")
    

def geraLink(email: str, url_base: str):
    # Data de validade do token
    validade = datetime.utcnow() + TOKEN_VALIDADE
    # Gera o token
    token_info = {"email": email, "validade": validade.timestamp()}
    token = jwt.encode(token_info, SECRET_KEY)

    # Gera o link para a troca de senha
    url = url_base + "/troca-senha/" + token
    return url

