from app.controllers.usuario import trocaSenhaControlador

from fastapi import APIRouter, HTTPException, status, Response


roteador = APIRouter(prefix="/usuarios", tags=["Usuários"])


@roteador.post(
    "/troca-senha/{token}",
    name="Trocar senha",
    description="""
        Altera a senha do usuário. Falha, se a senha ou o link forem inválidos.
    """,
    status_code=status.HTTP_200_OK,
)
def trocaSenha(token, response: Response):
    # Despacha o token para o controlador
    retorno = trocaSenhaControlador(token)

    response.status_code = retorno.get("status")
    return {"mensagem": retorno.get("mensagem")}
