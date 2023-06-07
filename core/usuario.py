from app.models.usuarioBD import UsuarioBD
from core.autenticacao import hashSenha

import logging


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
