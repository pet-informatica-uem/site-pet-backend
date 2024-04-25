import fnmatch
import os
from pathlib import Path
import time
from typing import BinaryIO

import PyPDF2
from pdf2image import convert_from_bytes
from PIL import Image

from src.config import config


def validaImagem(imagem: bytes | BinaryIO | str) -> bool:
    """Retorna se 'imagem' é válida.

    :param imagem -- a imagem em si ou o caminho da imagem

    :return -- valor booleano
    """
    eh_valida = True
    try:
        with Image.open(imagem) as img:
            if img.format not in ["PNG", "JPEG"]:
                eh_valida = False
    except IOError:
        return False

    return eh_valida


def validaComprovante(comprovante: bytes | BinaryIO | str) -> bool:
    """Retorna se 'comprovante' é válido.

    :param comprovante -- o comprovante em si ou o caminho do comprovante

    :return -- valor booleano
    """
    eh_valida = True

    try:
        with Image.open(comprovante) as img:
            if img.format not in ["PNG", "JPEG", "PDF"]:
                eh_valida = False
    except IOError:
        try:
            # Abre o PDF
            pdf_reader = PyPDF2.PdfReader(comprovante)  # type: ignore

            # Checa se o PDF está criptografado
            if pdf_reader.is_encrypted:
                return False
        except Exception as e:
            return False

    return eh_valida


def armazenaFotoUsuario(idUsuario: str, arquivo: str | bytes | BinaryIO) -> Path | None:
    """Armazena a imagem em "images/usuario" usando um nome base para o arquivo.

    :param idUsuario -- nome do usuario relacionado a imagem
    :param arquivo -- a imagem em si

    :return -- caminho para a imagem salva -> str. None, se a imagem for inválida.
    """
    path = config.CAMINHO_IMAGEM / "usuarios"
    retorno = __armazenaImagem(path, idUsuario, arquivo)

    return retorno


def armazenaArteEvento(idEvento: str, arquivo: bytes | BinaryIO) -> Path | None:
    """Armazena a imagem em "images/eventos/{evento}/arte" usando um nome base para o arquivo.

    :param idEvento -- nome do evento relacionada a imagem
    :param arquivo -- a imagem em si

    :return -- caminho para a imagem salva -> str. None, se a imagem for inválida.
    """
    path = config.CAMINHO_IMAGEM / "eventos" / idEvento / "arte"
    retorno = __armazenaImagem(path, idEvento, arquivo)

    return retorno


def armazenaCrachaEvento(idEvento: str, arquivo: bytes | BinaryIO) -> Path | None:
    """Armazena a imagem em "images/eventos/{evento}/cracha" usando um nome base para o arquivo.

    :param idEvento -- nome do evento relacionado a imagem
    :param arquivo -- a imagem em si

    :return -- caminho para a imagem salva -> str. None, se a imagem for inválida.
    """
    path = config.CAMINHO_IMAGEM / "eventos" / idEvento / "cracha"
    retorno = __armazenaImagem(path, idEvento, arquivo)

    return retorno


def armazenaComprovante(
    idEvento: str, idUsuario: str, arquivo: bytes | BinaryIO
) -> Path | None:
    """Armazena a imagem em "images/eventos/{evento}/comprovantes" usando um nome base para o arquivo.

    :param idEvento -- nome do evento relacionado ao comprovante
    :param idUsuario -- id do usuário relacionado ao comprovante
    :param arquivo -- o comprovante em si

    :return -- caminho para o comprovante salvo -> str. None, se o comprovante for inválido.
    """
    path = config.CAMINHO_IMAGEM / "eventos" / idEvento / "comprovantes"
    retorno = __armazenaComprovante(path, idUsuario, arquivo)

    return retorno


def procuraImagem(nomeImagem: str, searchPath: list[str] = []) -> list[Path]:
    """Retorna uma lista com os caminhos para as imagens que
    contenham 'nomeImagem' em seu nome. Retorna uma lista vazia
    caso não encontre nada.

    :param nomeImagem -- nome da imagem a ser procurada
    :param serchPath -- caminho onde buscar a imagem(s)

    :return -- lista contendo os caminhos das imagens encontradas
    """

    path = config.CAMINHO_IMAGEM
    if searchPath:
        path = path.joinpath(*searchPath)

    matches = [p for p in path.rglob(f"*{nomeImagem}*") if p.is_file()]
    return matches


def deletaImagem(nomeImagem: str, path: list[str] = []) -> list[Path] | None:
    """Deleta uma imagem. Caso seja encontrado mais de uma imagem com o termo de busca, todas serão deletadas.

    :param nomeImagem -- nome da imagem para ser removida
    :param path -- caminho onde procurar e deletar

    :return -- lista com o caminho de todas as imagens deletadas, None caso nada tenha sido deletado.
    """
    imagens = procuraImagem(nomeImagem, path)
    if imagens:
        deletados: list[Path] = []
        for imagem in imagens:
            imagem.unlink()
            deletados.append(imagem)
        return deletados
    return None


def __armazenaImagem(
    path: Path, nomeBase: str, imagem: bytes | BinaryIO | str
) -> Path | None:
    """Armazena a imagem no path fornecido usando um nome base.

    :param path -- caminho onde será armazenado a imagem
    :param nomeBase -- nome como será salvo a imagem
    :param imagem -- a imagem em si que será salva

    :return -- caminho para a imagem salva : str. None, se a imagem for inválida.
    """

    try:
        with Image.open(imagem, formats=["PNG", "JPEG"]) as img:
            extensao = img.format.lower()  # type: ignore
            nome = __geraNomeImagem(nomeBase, extensao=extensao)
            pathDefinitivo = path / nome
            img.save(pathDefinitivo)
        return pathDefinitivo
    except IOError:
        return None


def __armazenaComprovante(
    path: Path, nomeBase: str, comprovante: bytes | BinaryIO | str
) -> Path | None:
    """Armazena o comprovante no path fornecido usando um nome base.

    :param path -- caminho onde será armazenado o comprovante
    :param nomeBase -- nome como será salvo o comprovante
    :param imagem -- o comprovante em si que será salvo

    :return -- caminho para o comprovante salvo : str. None, se o comprovante for inválido.
    """
    try:
        with Image.open(comprovante, formats=["PNG", "JPEG"]) as img:
            extensao = img.format.lower()  # type: ignore
            nome = __geraNomeImagem(nomeBase, extensao=extensao)
            pathDefinitivo = path / nome
            img.save(pathDefinitivo)
        return pathDefinitivo
    except IOError:
        try:
            # Abre o PDF
            arquivo_pdf = comprovante.read()

            # Coloca as imagens do PDF na memória
            imagens = convert_from_bytes(arquivo_pdf)
            
            # Converte as imagens para RGB
            for image in imagens:
                if image.mode != "RGB":
                    image = image.convert("RGB")

            # Define o tamanho e largura maximo das imagens
            largura_saida = max(image.width for image in imagens)
            altura_saida = sum(image.height for image in imagens)

            # Cria a imagem de saída
            imagem_saida = Image.new("RGB", (largura_saida, altura_saida))

            # Concatena as imagens na vertical
            pos_y = 0
            for imagem_chunk in imagens:
                imagem_saida.paste(imagem_chunk, (0, pos_y))
                pos_y += imagem_chunk.height

            # Salva a imagem de saída
            nome = __geraNomeImagem(nomeBase, "png")
            pathDefinitivo = os.path.join(path, nome)
            imagem_saida.save(pathDefinitivo)

        except Exception as e:
            return None


def __geraNomeImagem(nomeBase: str, extensao: str) -> str:
    """Gera um nome para a imagem a partir de um nome base e uma extensao,
    adiciona uma timestamp para evitar problemas com o cache do navegador

    :param nomeBase -- nome base para gerar o novo nome
    :param extensao -- extensao da imagem

    :return -- nome como será salva a imagem
    """
    estampa = int(time.time())
    nome = f"{nomeBase}-{estampa}.{extensao}"

    return nome
