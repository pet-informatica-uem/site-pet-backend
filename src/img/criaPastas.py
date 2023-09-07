import logging
import os


def criaPastas():
    """Cria a estrutura de pastas para armazenar as imagens, caso já não exista."""
    directories = [
        "img",
        "img/usuarios",
        "img/eventos",
    ]

    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
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
        if not os.path.exists(directory):
            os.makedirs(directory)
            logging.info(f"Created directory: {directory}")
