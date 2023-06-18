from datetime import datetime, timedelta

from app.controllers.operacoesEmail import verificarEmail
from app.model.usuarioBD import UsuarioBD
from core.config import config
from core.jwtoken import geraTokenAtivaConta, processaTokenAtivaConta
from core.usuario import ativaconta, hashSenha


def ativaContaControlador(token: str) -> dict:
    """
    Recebe um token JWT de ativação de conta.

    Caso o token seja válido, ativa a conta e retorna um dicionário
    com campo "status" igual a "200".

    Caso contrário, retorna um dicionário com campo "status" diferente
    de "200" e um campo "mensagem" contendo uma mensagem de erro.
    """

    # Verifica o token e recupera o email
    retorno = processaTokenAtivaConta(token)
    if retorno.get("status") != "200":
        return retorno

    # Ativa a conta no BD
    msg = retorno.get("mensagem")
    assert msg is not None  # tipagem
    id = msg["idUsuario"]
    email = msg["email"]

    retorno = ativaconta(id, email)

    return retorno


def cadastraUsuarioControlador(
    nomeCompleto: str, cpf: str, email: str, senha: str, curso: str | None
) -> dict:
    """
    Cria uma conta com os dados fornecidos, e envia um email
    de confirmação de criação de conta ao endereço fornecido.

    Este controlador assume que o cpf e email já estão nas formas
    normalizadas (cpf contendo 11 dígitos, email sem espaço em branco
    prefixado ou sufixado e com todos os caracteres em caixa baixa).

    Retorna um dicionário contendo campos "status" e "mensagem".

    - Se a conta foi criada com sucesso, "status" == "201" e "mensagem" conterá
    o _id da conta (str).
    - Se a conta não foi criada com sucesso, "status" != "201" e "mensagem" conterá
    uma mensagem de erro (str).

    A criação da conta pode não suceder por erro na validação de dados,
    por já haver uma conta cadastrada com tal CPF ou email ou por falha
    de conexão com o banco de dados.
    """

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
    token = geraTokenAtivaConta(id, email, timedelta(days=1))

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
