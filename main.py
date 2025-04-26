import locale
import logging
import logging.handlers

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import config
from src.img.criaPastas import criaPastas
from src.limiter import limiter
from src.middleware.excecoes import ExcecaoAPIMiddleware
from src.middleware.logger import LoggerMiddleware
from src.middleware.tamanhoLimite import TamanhoLimiteMiddleware
from src.middleware.tempoLimite import TempoLimiteMiddleware
from src.rotas.evento.eventoRotas import roteador as roteadorEvento
from src.rotas.img.imgRotas import roteador as roteadorImg
from src.rotas.inscrito.inscritoRotas import roteador as roteadorInscrito
from src.rotas.usuario.usuarioRotas import roteador as roteadorUsuario
from src.recepcao.rotas import roteador as roteadorRecepcao
from src.capacitacao.rotas import roteador as roteadorCapacitacao

## Configuração dos logs.
criaPastas()

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

## Domínios permitidos no CORS.
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
    "https://recepcao-calouros-2025.vercel.app",
]

petBack = FastAPI(root_path=config.ROOT_PATH)
petBack.state.limiter = limiter

## Configura os middlewares. Para mais detalhes, confira o documento
## [docs/middlewares.md](docs/middlewares.md).
petBack.add_middleware(ExcecaoAPIMiddleware)
petBack.add_middleware(LoggerMiddleware)
petBack.add_middleware(TempoLimiteMiddleware, request_timeout=30)
petBack.add_middleware(TamanhoLimiteMiddleware, size_limit=5 * 1024 * 1024)

## Adiciona os módulos do site.
petBack.include_router(roteadorUsuario)
petBack.include_router(roteadorEvento)
petBack.include_router(roteadorInscrito)
petBack.include_router(roteadorImg)
petBack.include_router(roteadorRecepcao)
petBack.include_router(roteadorCapacitacao)

petBack.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
