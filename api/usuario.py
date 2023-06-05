from app.controllers.usuario import trocaSenhaControlador

from fastapi import APIRouter, HTTPException, status


roteador = APIRouter(prefix="/usuarios", tags=["Usuários"])


@roteador.post(
    "/troca-senha/{token}",
    name="Trocar senha",
    description="""
        Altera a senha do usuário. Falha, se a senha ou o link forem inválidos.
    """,
    status_code=status.HTTP_200_OK,
)
def trocaSenha(token):
    # Despacha o token para o controlador
    sucesso, msg = trocaSenhaControlador(token)

    match (sucesso, msg):
        case (False, "interno"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Problema interno.",
            )

        case (False, "expirou"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Link expirou."
            )

        case (True, ""):
            return {"menssagem": "sucesso"}
