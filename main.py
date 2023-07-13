import locale
import logging

from fastapi import FastAPI

from src.img.criaPastas import criaPastas
from src.rotas.evento.eventoRotas import roteador as roteadorEvento
from src.rotas.petiano.petianoRotas import roteador as roteadorPetianos
from src.rotas.usuario.usuarioRotas import roteador as roteadorUsuario

logging.basicConfig(
    handlers=[
        logging.FileHandler("output.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
    encoding="utf-8",
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")

# Caso não existam, cria as pastas para armazenar imagens.
criaPastas()

petBack = FastAPI()
petBack.include_router(roteadorUsuario)
petBack.include_router(roteadorPetianos)
petBack.include_router(roteadorEvento)

logging.info("Backend inicializado")
