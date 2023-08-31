import locale
import logging

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import config
from src.img.criaPastas import criaPastas
from src.middlewareExcecao import requestHandler as middlewareExcecao
from src.rotas.evento.eventoRotas import roteador as roteadorEvento
from src.rotas.inscrito.inscritoRotas import roteador as roteadorInscrito
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
origins = ["http://localhost:3000", "http://localhost"]

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
petBack.include_router(roteadorEvento)
petBack.include_router(roteadorInscrito)

# Caso não existam, cria as pastas para armazenar imagens.
criaPastas()

logging.info("Backend inicializado")

# Quando rotinas forem necessárias no futuro, usar o código abaixo como exemplo.
# # Inicializa o scheduler
# scheduler = BackgroundScheduler()
# scheduler.start()

# # Adiciona a rotina de verificação de eventos finalizados
# scheduler.add_job(
#     verificaEventosFinalizados,
#     "interval",
#     days=1,
#     start_date=config.HORARIO_INICIO_ROTINAS,  # Inicia a rotina no horário definido
# )
