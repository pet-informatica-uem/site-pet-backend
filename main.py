import logging, locale

from fastapi import FastAPI

from api import roteadorUsuario, roteadorPetianos, roteadorEvento

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

petBack = FastAPI()
petBack.include_router(roteadorUsuario)
petBack.include_router(roteadorPetianos)
petBack.include_router(roteadorEvento)

logging.info("Backend inicializado")
