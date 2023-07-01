from api import roteadorUsuario, roteadorEvento

import logging
from fastapi import FastAPI
from api import roteadorEvento

petBack = FastAPI()
petBack.include_router(roteadorUsuario)
petBack.include_router(roteadorEvento)

logging.basicConfig(
    filename="output.log",
    encoding="utf-8",
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logging.info("Backend inicializado")
