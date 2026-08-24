"""Operações relacionadas à geração de QR Codes."""

from io import BytesIO

import qrcode
from qrcode.constants import ERROR_CORRECT_M


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