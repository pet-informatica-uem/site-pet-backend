from core.jwtoken import processaTokenAtivaConta
from core.usuario import ativaconta

def ativaContaControlador(token: str) -> dict:
    # Verifica o token e recupera o email
    retorno = processaTokenAtivaConta(token)
    if retorno.get("status") != "200":
        return retorno

    # Ativa a conta no BD
    email = retorno.get("email")
    retorno = ativaconta(email)

    return retorno
