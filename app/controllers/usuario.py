from datetime import datetime
import logging

import jwt

from app.models.usuarioBD import UsuarioBD
from core.autenticacao import hashSenha

# Palavra chave para assinar o token
SECRET_KEY = "P#%w5R9h@#6eG&i@"


def trocaSenhaControlador(token, senha: str) -> dict:
    # Verifica o token e recupera o email
    retorno = processaTokenTrocaSenha(token)
    if retorno.get("status") != "200":
        return retorno

    # Atualiza a senha no bd
    email = retorno.get("email")
    retorno = autalizaSenha(email, senha)

    return retorno


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


def autalizaSenha(email: str, senha: str) -> dict:
    try:
        conexao = UsuarioBD()

        # Recupera o id a partir do email
        id = conexao.getIdUsuario(email)

        # Atualiza a senha
        conexao.setSenhaUsuario(id, hashSenha(senha))

        logging.info("Senha atualizada para o usuário com ID: " + id)
        return {"mensagem": "Usuário atualizado.", "status": "200"}

    except Exception as e:
        logging.warning("Erro no banco de dados: " + str(e))
        return {"mensagem": "Erro interno.", "status": "500"}
