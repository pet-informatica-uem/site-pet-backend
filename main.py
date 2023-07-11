import logging, locale

from fastapi import FastAPI

from api import roteadorEvento, roteadorPetianos, roteadorUsuario
from core.criaPastas import criaPastas

logging.basicConfig(
    handlers=[
        logging.FileHandler("output.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
    encoding="utf-8",
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

# Caso não existam, cria as pastas para armazenar imagens.
criaPastas()

petBack = FastAPI()
petBack.include_router(roteadorUsuario)
petBack.include_router(roteadorPetianos)
petBack.include_router(roteadorEvento)

logging.info("Backend inicializado")
