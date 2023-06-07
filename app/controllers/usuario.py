from core.jwtoken import processaTokenTrocaSenha
from core.usuario import autalizaSenha


def trocaSenhaControlador(token, senha: str) -> dict:
    # Verifica o token e recupera o email
    retorno = processaTokenTrocaSenha(token)
    if retorno.get("status") != "200":
        return retorno

    # Atualiza a senha no bd
    email = retorno.get("email")
    retorno = autalizaSenha(email, senha)

    return retorno

