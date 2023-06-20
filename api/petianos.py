from app.controllers.petianos import infoPetianos

from fastapi import APIRouter

roteador = APIRouter(tags=["Petianos"])

@roteador.get("/petianos")
async def lerPetianos():
    return infoPetianos()