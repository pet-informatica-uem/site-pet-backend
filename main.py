from api import roteadorUsuario

import logging
from fastapi import FastAPI

logging.basicConfig(
    filename="output.log",
    encoding="utf-8",
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

petBack = FastAPI()
petBack.include_router(roteadorUsuario)

logging.info("Backend inicializado")
