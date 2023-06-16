from app.model.usuarioBD import UsuarioBD

import logging

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hashSenha(senha: str) -> str:
    return pwd_context.hash(senha)


def verificaSenha(senha: str, hash: str) -> bool:
    return pwd_context.verify(senha, hash)


def ativaconta(id: str, email: str) -> dict:
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
