from core.operacoesImagem import armazenaArteEvento, armazenaArteQrCodeEvento, validaImagem

from fastapi import UploadFile

from typing import Dict

def controladorNovoEvento(dadosEvento: dict, imagens: Dict[str, UploadFile]) -> dict:
    # TODO Valida os dados do evento

    # Valida as imagens
    if not validaImagem(imagens.get("arte").file):
        return {"mensagem": "Imagem da arte inválida.", "status": "400"}

    if imagens.get("qrcode"):
        if not validaImagem(imagens.get("qrcode").file):
            return {"mensagem": "Imagem do QrCode inválida.", "status": "400"}

    # TODO Registra o evento no bd

    # TODO Armazena as imagens
    pass
