import locale
import logging
import logging.handlers

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import config
from src.img.criaPastas import criaPastas
from src.middleware import requestHandler, requestLogger
from src.rotas.evento.eventoRotas import roteador as roteadorEvento
from src.rotas.inscrito.inscritoRotas import roteador as roteadorInscrito
from src.rotas.usuario.usuarioRotas import roteador as roteadorUsuario

logging.basicConfig(
    handlers=[
        logging.handlers.TimedRotatingFileHandler(
            "logs/output.log", when="midnight", interval=1
        ),
        logging.StreamHandler(),
    ],
    encoding="utf-8",
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")
origins = ["*"]

petBack = FastAPI(root_path=config.ROOT_PATH)

petBack.middleware("http")(requestHandler)
petBack.middleware("http")(requestLogger)
petBack.include_router(roteadorUsuario)
petBack.include_router(roteadorEvento)
petBack.include_router(roteadorInscrito)

petBack.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
