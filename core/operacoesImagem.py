import fnmatch
import time, os

from PIL import Image


IMAGES_PATH = os.path.join(
    os.path.abspath(os.path.dirname(os.path.dirname(__file__))), "images"
)


def validaImagem(imagem: str | bytes) -> bool:
    "Retorna True se o arquivo for uma imagem válida. False, caso contrário."

    try:
        img = Image.open(imagem)
        img.close()
        return True
    except IOError:
        return False


def armazenaArteEvento(nomeEvento: str, arquivo: str | bytes) -> str:
    """Armazena a imagem em "images/eventos/arte" usando um nome base para o arquivo.

    Return: caminho para a imagem salva : str. None, se a imagem for inválida.
    """
    path = os.path.join(IMAGES_PATH, "eventos", "arte")
    retorno = __armazenaImagem(path, nomeEvento, arquivo)

    return retorno


def armazenaQrCodeEvento(nomeEvento: str, arquivo: str | bytes) -> str:
    """Armazena a imagem em "images/eventos/qrcode" usando um nome base para o arquivo.

    Return: caminho para a imagem salva : str. None, se a imagem for inválida.
    """
    path = os.path.join(IMAGES_PATH, "eventos", "qrcode")
    retorno = __armazenaImagem(path, nomeEvento, arquivo)

    return retorno


def procuraImagem(nomeImagem: str) -> list[str]:
    """ "Retorna uma lista com os caminhos para as imagens que
    contenham "nomeImagem" em seu nome. Retorna uma lista vazia
    caso não encontre nada."""

    ls = os.walk(IMAGES_PATH)
    matches = []
    for grupo in ls:
        root, dirs, files = grupo
        for file in files:
            if fnmatch.fnmatch(file, f"*{nomeImagem}*"):
                matches.append(os.path.join(root, file))
    return matches


def deletaImagem(nomeImagem: str) -> dict:
    """Deleta uma imagem. Caso seja encontrada mais de uma imagem 
    com o termo de busca, todas serão deletadas.

    nomeImagem -- nome da imagem para ser removida

    Return:
    \n"status": "200" se deu certo.
    \n"status": "404" se não encontrou imagem com esse nome.
    """
    imagens = procuraImagem(nomeImagem)
    if (imagens):
        for imagem in imagens:
            os.remove(imagem)
        return {"mensagem": "Imagem(s) deleta(s) com sucesso!", "status": "200"}
    return {"mensagem": "Nenhuma imagem encontrada.", "status": "404"}


def __armazenaImagem(path: str, nomeBase: str, imagem: str | bytes) -> str:
    """Armazena a imagem no path fornecido usando um nome base.

    Return: caminho para a imagem salva : str. None, se a imagem for inválida.
    """

    try:
        img = Image.open(imagem)
        extensao = img.format.lower()
        nome = __geraNomeImagem(nomeBase, extensao=extensao)
        pathDefinitivo = os.path.join(path, nome)
        img.save(pathDefinitivo)
        img.close()
        return pathDefinitivo
    except IOError:
        return None


def __geraNomeImagem(nomeBase: str, extensao: str) -> str:
    """Gera um nome para a imagem a partir de um nome base e uma extensao,
    adiciona uma timestamp para evitar problemas com o cache do navegador
    """
    estampa = int(time.time())
    nome = f"{nomeBase}-{estampa}.{extensao}"

    return nome
