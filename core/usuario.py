from app.model.usuarioBD import UsuarioBD
from core.autenticacao import hashSenha

import logging


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


def verificaSeUsuarioExiste(email: str) -> dict:
    """
    Verifica se existe usuário associado a um email.

    Parâmetros:
        email (str): email a ser verificado

    Retorno:
        dict:
            - {"mensagem": True, "status": "200"}: Existe usuário associado.

            - {"mensagem": False, "status": "404"}: Não existe usuário associado.

            - {"mensagem": "Erro interno", "status": "500"}: Problema no banco de dados.
    """

    try:
        conexao = UsuarioBD()

        # Verifica se existe usuário com esse email
        if conexao.getIdUsuario(email)["status"] == "404":
            return {"mensagem": False, "status": "404"}
        return {"mensagem": True, "status": "200"}

    except Exception as e:
        logging.warning("Erro no banco de dados: " + str(e))
        return {"mensagem": "Erro interno.", "status": "500"}


def atualizaSenha(email: str, senha: str) -> dict:
    try:
        conexao = UsuarioBD()

        # Recupera os dados do usuário a partir do email
        idUsuario = conexao.getIdUsuario(email)["mensagem"]
        dadosUsuario = conexao.getUsuario(idUsuario)["mensagem"]

        # Atualiza a senha
        dadosUsuario["senha"] = hashSenha(senha)
        conexao.atualizarUsuario(idUsuario, dadosUsuario)

        logging.info("Senha atualizada para o usuário com ID: " + str(id))
        return {"mensagem": "Usuário atualizado.", "status": "200"}

    except Exception as e:
        logging.warning("Erro no banco de dados: " + str(e))
        return {"mensagem": "Erro interno.", "status": "500"}
