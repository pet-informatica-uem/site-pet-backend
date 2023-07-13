import logging
import os


def criaPastas():
    directories = [
        "img",
        "img/usuarios",
        "img/eventos",
        "img/eventos/arte",
        "img/eventos/qrcode",
    ]

    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            logging.info(f"Created directory: {directory}")
