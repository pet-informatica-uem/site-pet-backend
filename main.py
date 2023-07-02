import logging

from fastapi import FastAPI

from api import roteadorEvento, roteadorPetianos, roteadorUsuario

petBack = FastAPI()
petBack.include_router(roteadorUsuario)


logging.basicConfig(
    handlers=[
        logging.FileHandler("output.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
    encoding="utf-8",
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

petBack = FastAPI()
petBack.include_router(roteadorUsuario)
petBack.include_router(roteadorPetianos)
petBack.include_router(roteadorEvento)

logging.info("Backend inicializado")
