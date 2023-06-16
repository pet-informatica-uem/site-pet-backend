from datetime import datetime, timedelta
import logging
from app.controllers.operacoesEmail import verificarEmail

from app.model.usuarioBD import UsuarioBD
from core import jwtoken
from core.config import config
from core.jwtoken import processaTokenAtivaConta
from core.usuario import ativaconta, hashSenha


def ativaContaControlador(token: str) -> dict:
    # Verifica o token e recupera o email
    retorno = processaTokenAtivaConta(token)
    if retorno.get("status") != "200":
        return retorno

    # Ativa a conta no BD
    id = retorno.get("idUsuario")
    email = retorno.get("email")
    assert id is not None
    assert email is not None

    retorno = ativaconta(id, email)

    return retorno


def cadastraUsuarioControlador(
    nomeCompleto: str, cpf: str, email: str, senha: str, curso: str | None
) -> dict:
    # 3. verifico se o email já existe e crio o usuário
    bd = UsuarioBD()
    resultado = bd.criarUsuario(
        {
            "nome": nomeCompleto,
            "email": email,
            "cpf": cpf,
            "curso": curso or "",
            "estado da conta": "inativo",
            "senha": hashSenha(senha),
            "tipo conta": "estudante",
            "data criacao": datetime.now(),
        }
    )

    if resultado["status"] != "200":
        return resultado

    id = str(resultado["mensagem"])

    # 4. gera token de ativação válido por 24h
    token = jwtoken.geraTokenAtivaConta(id, email, timedelta(days=1))

    # 5. manda email de ativação
    # não é necessário fazer urlencode pois jwt é url-safe
    linkConfirmacao = config.CAMINHO_BASE + "/usuario/confirmacaoEmail?token=" + token
    # print(linkConfirmacao)
    resultado = verificarEmail(
        config.EMAIL_SMTP, config.SENHA_SMTP, email, linkConfirmacao
    )

    if resultado["status"] != "200":
        # return {"status": "400", "mensagem": "Erro no envio do email."}
        # não indicar que o email não existe para evitar spam
        pass

    return {"status": "201", "mensagem": id}
