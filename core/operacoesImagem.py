import fnmatch
import os
import time
from typing import BinaryIO

from PIL import Image

from core.config import config


def validaImagem(imagem: bytes | BinaryIO):
    eh_valida = True
    try:
        with Image.open(imagem) as img:
            if img.format not in ["PNG", "JPEG"]:
                eh_valida = False
    except IOError:
        return False

    return eh_valida



def armazenaArteEvento(nomeEvento: str, arquivo: bytes | BinaryIO) -> str | None:
    """Armazena a imagem em "images/eventos/arte" usando um nome base para o arquivo.

    Return: caminho para a imagem salva -> str. None, se a imagem for inválida.
    """
    path = os.path.join(config.CAMINHO_IMAGEM, "eventos", "arte")
    retorno = __armazenaImagem(path, nomeEvento, arquivo)

    return retorno



def armazenaFotoUsuario(nomeUsuario: str, arquivo: str | bytes) -> str | None:
    """Armazena a imagem em "images/usuario" usando um nome base para o arquivo.

    Return: caminho para a imagem salva -> str. None, se a imagem for inválida.
    """
    path = os.path.join(IMAGES_PATH, "usuarios")
    retorno = __armazenaImagem(path, nomeUsuario, arquivo)

    return retorno


def armazenaQrCodeEvento(nomeEvento: str, arquivo: bytes | BinaryIO) -> str | None:
    """Armazena a imagem em "images/eventos/qrcode" usando um nome base para o arquivo.

    Return: caminho para a imagem salva -> str. None, se a imagem for inválida.
    """
    path = os.path.join(config.CAMINHO_IMAGEM, "eventos", "qrcode")
    retorno = __armazenaImagem(path, nomeEvento, arquivo)

    return retorno


def procuraImagem(nomeImagem: str, searchPath: list[str] = []) -> list[str]:
    """Retorna uma lista com os caminhos para as imagens que
    contenham 'nomeImagem' em seu nome. Retorna uma lista vazia
    caso não encontre nada."""

    path = config.CAMINHO_IMAGEM
    if searchPath:
        path = os.path.join(config.CAMINHO_IMAGEM, *searchPath)

    ls = os.walk(path)
    matches = []
    for grupo in ls:
        root, dirs, files = grupo
        for file in files:
            if fnmatch.fnmatch(file, f"*{nomeImagem}*"):
                matches.append(os.path.join(root, file))
    return matches


def deletaImagem(nomeImagem: str, path: list[str] = []) -> dict:
    """Deleta uma imagem. Caso seja encontrado mais de uma imagem com o termo de busca, todas serão deletadas.

    :param nomeImagem -- nome da imagem para ser removida

    :return: "status": "200"(OK) | "status": "404" (Not Found).
    """
    imagens = procuraImagem(nomeImagem, path)
    if imagens:
        for imagem in imagens:
            os.remove(imagem)
        return {"mensagem": "Imagem(s) deleta(s) com sucesso!", "status": "200"}
    return {"mensagem": "Nenhuma imagem encontrada.", "status": "404"}



def __armazenaImagem(path: str, nomeBase: str, imagem: bytes | BinaryIO) -> str | None:
    """Armazena a imagem no path fornecido usando um nome base.

    Return: caminho para a imagem salva : str. None, se a imagem for inválida.
    """

    try:
        with Image.open(imagem, formats=["PNG", "JPEG"]) as img:
            extensao = img.format.lower()
            nome = __geraNomeImagem(nomeBase, extensao=extensao)
            pathDefinitivo = os.path.join(path, nome)
            img.save(pathDefinitivo)
        return pathDefinitivo
    except IOError as e:
        return None


def __geraNomeImagem(nomeBase: str, extensao: str) -> str:
    """Gera um nome para a imagem a partir de um nome base e uma extensao,
    adiciona uma timestamp para evitar problemas com o cache do navegador
    """
    estampa = int(time.time())
    nome = f"{nomeBase}-{estampa}.{extensao}"

    return nome
