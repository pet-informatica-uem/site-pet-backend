import locale
import logging

from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.middleware.tamanhoLimite import TamanhoLimiteMiddleware
from src.middleware.tempoLimite import TempoLimiteMiddleware
from src.config import config
from src.img.criaPastas import criaPastas
from src.middleware.excecoes import ExcecaoAPIMiddleware
from src.rotas.evento.eventoRotas import roteador as roteadorEvento
from src.rotas.inscrito.inscritoRotas import roteador as roteadorInscrito
from src.rotas.usuario.usuarioRotas import roteador as roteadorUsuario
from src.limiter import limiter

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
    "http://localhost:3000",
    "https://localhost:3000",
    "http://localhost",
    "https://localhost",
    "http://localhost:8000",
    "https://localhost:8000",
    "http://www.din.uem.br",
    "https://www.din.uem.br",
    "https://www.petinfouem.com.br",
]

petBack = FastAPI(root_path=config.ROOT_PATH)
petBack.state.limiter = limiter

petBack.add_middleware(TamanhoLimiteMiddleware, size_limit=5 * 1024 * 1024)
petBack.add_middleware(BaseHTTPMiddleware, dispatch=TempoLimiteMiddleware(30))
petBack.add_middleware(BaseHTTPMiddleware, dispatch=ExcecaoAPIMiddleware)
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
