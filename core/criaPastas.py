import logging
import os


def criaPastas():
    directories = [
        "images",
        "images/usuarios",
        "images/eventos",
        "images/eventos/arte",
        "images/eventos/qrcode",
    ]

    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            logging.info(f"Created directory: {directory}")
