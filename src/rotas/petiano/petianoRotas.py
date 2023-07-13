from fastapi import APIRouter

from rotas.petiano.petianoControlador import infoPetianos

roteador = APIRouter(tags=["Petianos"])


@roteador.get("/petianos")
async def lerPetianos():
    return infoPetianos()
