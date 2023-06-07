from app.models.usuarioBD import UsuarioBD
from core import enviarEmail
from core.jwtoken import geraLink
from core.usuario import verificaSeUsuarioExiste

from datetime import datetime, timedelta

import jwt


# Envia um email para trocar de senha se o email estiver cadastrado no bd
def recuperaContaControlador(email: str, url_base: str) -> tuple:
    # Verifica se o usuário está cadastrado no bd
    retorno = verificaSeUsuarioExiste(email)
    if retorno.get("status") != "200":
        return retorno

    # Gera o link e envia o email se o usuário estiver cadastrado
    if retorno.get("existe"):
        link = geraLink(email, url_base)
        enviarEmail(email, link)
        return {"mensagem": "OK", "status": "200"}

