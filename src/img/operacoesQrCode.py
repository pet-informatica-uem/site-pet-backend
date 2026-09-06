"""Operações relacionadas a QR Codes."""

from io import BytesIO


import qrcode
from qrcode.constants import ERROR_CORRECT_M
from src.autenticacao.jwtoken import processaTokenPresencaEvento
from datetime import UTC, datetime


def geraQRCode(conteudo: str) -> bytes:
    """
    Gera um QR Code PNG em memória a partir do conteúdo fornecido.

    :param conteudo: Texto que será codificado no QR Code.
    :return: Bytes da imagem PNG gerada.
    """
    qr = qrcode.QRCode(
        version=None,
        error_correction=ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(conteudo)
    qr.make(fit=True)

    imagem = qr.make_image()
    buffer = BytesIO()
    imagem.save(buffer, format="PNG")

    return buffer.getvalue()


def leQRCode(token: str) -> dict[str, str | datetime]:
    """
    Le um Token e o transforma em um dicionário para permitir operações no banco de dados

    :param token: Texto que será decodificado em um dicionário
    :return: Identificadores validados e data_leitura gerada pelo servidor em UTC.
    """
    return processaTokenPresencaEvento(token) | {"data_leitura": datetime.now(UTC)}


def converteTimestamp(dicionario: dict, chave: str) -> dict:
    """
    Função que converte timeStamp em uma string de data e hora do tipo DD-MM-YYYY HH:MM:SS

    :param dicionario - Dicionário que contém a chave timestamp para ser convertida
    :param chave - Chave timestamp
    :return: O próprio dicionário com a chave no formato de string
    """
    leitura_convertida = datetime.fromtimestamp(dicionario[chave])
    dh_leitura_convertida = leitura_convertida.strftime('%d-%m-%Y %H:%M:%S')
    dicionario[chave] = dh_leitura_convertida
    return dicionario
