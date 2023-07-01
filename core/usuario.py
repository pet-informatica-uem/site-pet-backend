from app.model.usuarioBD import UsuarioBD

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


def verificaSeUsuarioExiste(email: str) -> dict:
    """
    Verifica se existe usuário associado a um email.

    Parâmetros:
        email (str): email a ser verificado

    Retorno:
        dict:
            \n- {"existe": True, "status": "200"}: Existe usuário associado. False, caso contrário.
            \n- {"mensagem": "Erro interno", "status": "500"}: Problema no banco de dados.
    """

    try:
        conexao = UsuarioBD()

        # Verifica se existe usuário com esse email
        if conexao.getIdUsuario(email) == "Usuário não encontrado":
            return {"existe": False, "status": "200"}
        return {"existe": True, "status": "200"}

    except Exception as e:
        logging.warning("Erro no banco de dados: " + str(e))
        return {"mensagem": "Erro interno.", "status": "500"}
