import locale
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.middlewareExcecao import requestHandler as middlewareExcecao
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
origins = [
    'http://localhost:3000',
    'http://localhost'
]

# Caso não existam, cria as pastas para armazenar imagens.
criaPastas()

origins = ["http://localhost:3000", "http://localhost"]

petBack = FastAPI()
petBack.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
petBack.middleware("http")(middlewareExcecao)
petBack.include_router(roteadorUsuario)
petBack.include_router(roteadorPetianos)
petBack.include_router(roteadorEvento)

logging.info("Backend inicializado")
