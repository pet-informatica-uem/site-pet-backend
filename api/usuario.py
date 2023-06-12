from app.controllers.usuario import trocaSenhaControlador
from core.ValidacaoCadastro import validaSenha

from fastapi import APIRouter, HTTPException, status, Response, Form

from typing import Annotated


roteador = APIRouter(prefix="/usuarios", tags=["Usuários"])


@roteador.post(
    "/troca-senha/{token}",
    name="Trocar senha",
    description="""
        Altera a senha do usuário. Falha, se a senha ou o link forem inválidos.
    """,
    status_code=status.HTTP_200_OK,
)
def trocaSenha(token, senha: Annotated[str, Form()],response: Response):
    # Validacao basica da senha
    if not validaSenha(senha, senha):
        raise HTTPException(
            status_code=400,
            detail="Senha inválida."
        )
    
    # Despacha o token para o controlador
    retorno = trocaSenhaControlador(token, senha)

    response.status_code = int(retorno.get("status"))
    return {"mensagem": retorno.get("mensagem")}
