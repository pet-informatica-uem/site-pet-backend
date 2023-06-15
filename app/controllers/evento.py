from core.operacoesImagem import armazenaArteEvento, armazenaQrCodeEvento, validaImagem
from app.models import EventoBD

from fastapi import UploadFile

from typing import Dict


def controladorNovoEvento(
    dadosEvento: dict, imagens: Dict[str, UploadFile] | None
) -> dict:
    # Valida as imagens
    if imagens:
        if not validaImagem(imagens.get("arte").file):
            return {"mensagem": "Imagem da arte inválida.", "status": "400"}

        if imagens.get("qrcode"):
            if not validaImagem(imagens.get("qrcode").file):
                return {"mensagem": "Imagem do QrCode inválida.", "status": "400"}

    # Armazena as imagens
    if imagens.get("arte"):
        caminhoArte = armazenaArteEvento(
            dadosEvento.get("nomeEvento"), imagens.get("arte").file
        )

    if imagens.get("qrcode"):
        caminhoQrCode = armazenaQrCodeEvento(
            dadosEvento.get("nomeEvento"), imagens.get("qrcode").file
        )

    # Valida os dados e registra o evento no bd
    dadosEvento["arte evento"] = caminhoArte
    dadosEvento["arte qrcode"] = caminhoQrCode

    try:
        conexao = EventoBD()
        retorno = conexao.cadastrarEvento(dadosEvento)
        if retorno.get("status") != "200":
            return retorno
        return {"mensagem": "Evento cadastrado com sucesso!", "status": "201"}
    except Exception as e:
        return {"mensagem": str(e), "status": "400"}
