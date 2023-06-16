from app.models.usuarioBD import UsuarioBD

import logging


def ativaconta(email: str) -> dict:
    try:
        conexao = UsuarioBD()

        # Recupera o id a partir do email
        id = conexao.getIdUsuario(email)

        # Atualiza a senha
        conexao.setEstado(id, "ativo")

        logging.info("Conta ativada para o usuário com ID: " + id)
        return {"mensagem": "Conta Ativada.", "status": "200"}

    except Exception as e:
        logging.warning("Erro no banco de dados: " + str(e))
        return {"mensagem": "Erro interno.", "status": "500"}