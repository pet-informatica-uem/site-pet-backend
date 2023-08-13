from fastapi import APIRouter

from src.rotas.petiano.petianoControlador import Petiano, infoPetianos

roteador = APIRouter(tags=["Petianos"])


@roteador.get(
    "/usuarios/petianos",
    name="Obter lista de petianos",
    description="Obtém uma lista de todos os petianos cadastrados no sistema.",
    response_model=list[Petiano],
)
def lerPetianos():
    return infoPetianos()
