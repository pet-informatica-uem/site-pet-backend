from fastapi import APIRouter, HTTPException
from app.controllers.inscritosEvento import InscritosEventoController

roteador = APIRouter(prefix="/eventos", tags=["Eventos"])


# recuperar dados do evento
@roteador.get(
    "/recuperar",
    name="Recuperar os inscritos de um determinado evento por ID",
    description="""
        Recupera os dados dos inscritos de um determinado evento, como pagamento, nome, email..
        Falha, caso o evento não exista o evento.
    """,
)
def recuperarInscritosEvento(idEvento: str) -> dict:

    inscritosController = InscritosEventoController()

    inscritos = inscritosController.getInscritosEvento(idEvento)
    print(inscritos)
    if inscritos.get("status") != "200":
        raise HTTPException(
            status_code=inscritos.get("status"), detail=inscritos.get("mensagem")
        )

    return {"mensagem": inscritos.get("mensagem")}