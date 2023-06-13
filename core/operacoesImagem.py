import time, os

from fastapi import UploadFile

from PIL import Image


IMAGES_PATH = os.path.join(
    os.path.abspath(os.path.dirname(os.path.dirname(__file__))), "images"
)


# Retorna True se o arquivo for uma imagem válida. False, caso contrário.
def validaImagem(imagem: bytes):
    try:
        img = Image.open(imagem)
        img.close()
        return True
    except IOError:
        return False


def armazenaArteEvento(nomeEvento: str, arquivo: UploadFile) -> dict:
    path = os.path.join(IMAGES_PATH, "eventos", "arte")
    retorno = __armazenaImagem(path, nomeEvento, arquivo)

    return retorno


def armazenaArteQrCodeEvento(nomeEvento: str, arquivo: UploadFile) -> dict:
    path = os.path.join(IMAGES_PATH, "eventos", "qrcode")
    retorno = __armazenaImagem(path, nomeEvento, arquivo)

    return retorno


def __armazenaImagem(path: str, nomeEvento: str, arquivo: UploadFile):
    try:
        img = Image.open(arquivo.file)
        extensao = arquivo.filename.split(".")[-1]
        nome = geraNomeImagem(nomeEvento, extensao=extensao)
        pathDefinitivo = os.path.join(path, nome)
        img.save(pathDefinitivo)
        img.close()
        return {"mensagem": "Imagem salva com sucesso.", "status": "201"}
    except IOError:
        return {"mensagem": "Imagem inválida.", "status": "400"}


# Gera um nome para a imagem a partir de um nome base e uma extensao,
# adiciona uma timestamp para evitar problemas com o cache do navegador
def geraNomeImagem(nomeBase: str, extensao: str) -> str:
    estampa = int(time.time())
    nome = f"{nomeBase}-{estampa}.{extensao}"

    return nome
