from app.models.usuarioBD import UsuarioBD

import logging


# Retorna true se o usuário existe. Caso contrário, retorna false. 
# Retorna uma mensagem de erro e status 500 se houver problema com a 
# comunicação com o banco de dados.
def verificaSeUsuarioExiste(email: str) -> dict:
    try:
        conexao = UsuarioBD()

        # Verifica se existe usuário com esse email
        if conexao.getIdUsuario(email) == "Usuário não encontrado":
            return {"existe": False, "status": "200"}
        return {"existe": True, "status": "200"}

    except Exception as e:
        logging.warning("Erro no banco de dados: " + str(e))
        return {"mensagem": "Erro interno.", "status": "500"}
