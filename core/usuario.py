import logging

from passlib.context import CryptContext

from app.model.usuarioBD import UsuarioBD

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hashSenha(senha: str) -> str:
    """
    Recebe uma senha e retorna o seu hash seguro.
    """
    return pwd_context.hash(senha)


def verificaSenha(senha: str, hash: str) -> bool:
    """
    Recebe uma senha e seu hash.
    Retorna um bool indicando se o hash corresponde à senha.
    """
    return pwd_context.verify(senha, hash)


def ativaconta(id: str, email: str) -> dict:
    """
    Recebe um id de usuário e um endereço de email e tenta
    mudar o estado da conta associada a esses dados para ativo.

    Falha caso não exista uma conta com o id indicado,
    caso exista uma conta mas ela possua um endereço de email
    diferente do indicado, caso a conta já esteja ativada
    ou caso ocorra algum erro interno decorrente do banco de dados.

    Retorna um dicionário contendo dois campos, "status" e "mensagem".
    - "status" == "200" se e somente se a conta foi ativada com sucesso.
    - "mensagem" contém uma mensagem informacional indicando sucesso
      ou o motivo do erro, caso este ocorra.
    """
    try:
        conexao = UsuarioBD()

        # Recupera o id a partir do email
        resp = conexao.getUsuario(id)
        if resp["status"] != "200":
            raise Exception(resp["mensagem"])

        usuario = resp["mensagem"]
        if usuario["email"] != email or usuario["estado da conta"] == "ativo":
            return {"mensagem": "Token expirada.", "status": "400"}

        # Atualiza a senha
        usuario["estado da conta"] = "ativo"
        del usuario["_id"]
        resp = conexao.atualizarUsuario(id, usuario)
        if resp["status"] != "200":
            raise Exception(resp["mensagem"])

        logging.info("Conta ativada para o usuário com ID: " + id)
        return {"mensagem": "Conta Ativada.", "status": "200"}

    except Exception as e:
        logging.warning("Erro no banco de dados: " + str(e))
        return {"mensagem": "Erro interno.", "status": "500"}
