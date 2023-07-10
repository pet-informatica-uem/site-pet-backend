from fastapi import APIRouter

from app.controllers.petianos import infoPetianos

roteador = APIRouter(tags=["Petianos"])


@roteador.get("/petianos")
async def lerPetianos():
    return infoPetianos()
