import logging
from modelos.excecao import NaoAutenticadoExcecao

from src.autenticacao.autenticacao import hashSenha
from src.modelos.usuario.usuarioBD import UsuarioBD


def ativaconta(id: str, email: str) -> None:
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
    conexao = UsuarioBD()

    # Recupera o id a partir do email
    usuario = conexao.getUsuario(id)
    if usuario["email"] != email or usuario["estado da conta"] == "ativo":
        raise NaoAutenticadoExcecao()

    # Atualiza a senha
    usuario["estado da conta"] = "ativo"
    del usuario["_id"]
    conexao.atualizarUsuario(id, usuario)

    logging.info("Conta ativada para o usuário com ID: " + id)


def verificaSeUsuarioExiste(email: str) -> str:
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

    conexao = UsuarioBD()

    # Verifica se existe usuário com esse email
    return conexao.getIdUsuario(email)
    


def atualizaSenha(email: str, senha: str) -> None:
    conexao = UsuarioBD()

    # Recupera os dados do usuário a partir do email
    idUsuario = conexao.getIdUsuario(email)
    dadosUsuario = conexao.getUsuario(idUsuario)

    # Atualiza a senha
    dadosUsuario["senha"] = hashSenha(senha)
    conexao.atualizarUsuario(idUsuario, dadosUsuario)

    logging.info("Senha atualizada para o usuário com ID: " + str(id))
