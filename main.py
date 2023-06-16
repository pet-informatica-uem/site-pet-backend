from fastapi import FastAPI
from api import usuario
import logging

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
petBack.include_router(usuario.usuario)
