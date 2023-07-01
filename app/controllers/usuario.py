from core.jwtoken import processaTokenAtivaConta, geraLink
from core.usuario import ativaconta, verificaSeUsuarioExiste
from app.controllers.operacoesEmail import resetarSenha


def ativaContaControlador(token: str) -> dict:
    # Verifica o token e recupera o email
    retorno = processaTokenAtivaConta(token)
    if retorno.get("status") != "200":
        return retorno

    # Ativa a conta no BD
    email = retorno.get("email")
    retorno = ativaconta(email)

    return retorno


EMAIL_PET = "pet@din.uem.br"
SENHA_EMAIL_PET = "0qvdd0Lw1JKF3lnRw6QU"


# Envia um email para trocar de senha se o email estiver cadastrado no bd
def recuperaContaControlador(email: str, url_base: str) -> dict:
    # Verifica se o usuário está cadastrado no bd
    retorno = verificaSeUsuarioExiste(email)
    if retorno.get("status") != "200":
        return retorno

    # Gera o link e envia o email se o usuário estiver cadastrado
    if retorno.get("existe"):
        link = geraLink(email, url_base)
        resetarSenha(EMAIL_PET, SENHA_EMAIL_PET, email, link)  # Envia o email

    return {"mensagem": "OK", "status": "200"}
