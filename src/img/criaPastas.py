import logging
from pathlib import Path


def criaPastas():
    """Cria a estrutura de pastas para armazenar as imagens, caso já não exista."""
    directories = [
        "img",
        "img/usuarios",
        "img/eventos",
    ]

    for directory in directories:
        path = Path.cwd() / directory
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            logging.info(f"Created directory: {directory}")


def criaPastaEvento(idEvento: str):
    """Cria a estrutura de pastas para armazenar as imagens, caso já não exista."""
    directories = [
        f"img/eventos/{idEvento}",
        f"img/eventos/{idEvento}/arte",
        f"img/eventos/{idEvento}/cracha",
        f"img/eventos/{idEvento}/comprovantes",
    ]

    for directory in directories:
        path = Path.cwd() / directory
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            logging.info(f"Created directory: {directory}")
