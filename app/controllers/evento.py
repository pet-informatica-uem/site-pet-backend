from core.operacoesImagem import armazenaArteEvento, armazenaQrCodeEvento, validaImagem, deletaImagem
from app.models import EventoBD
from app.models.evento import DadosEvento

from fastapi import UploadFile

import logging


def controladorNovoEvento(
    dadosEvento: DadosEvento, imagens: dict[str, UploadFile] | None
) -> dict:
    # Valida as imagens
    if imagens:
        if not validaImagem(imagens.get("arte").file):
            return {"mensagem": "Imagem da arte inválida.", "status": "400"}

        if imagens.get("qrcode"):
            if not validaImagem(imagens.get("qrcode").file):
                return {"mensagem": "Imagem do QrCode inválida.", "status": "400"}

    # Armazena as imagens
    caminhoArte = armazenaArteEvento(
        dadosEvento.get("nomeEvento"), imagens.get("arte").file
    )

    if imagens.get("qrcode"):
        caminhoQrCode = armazenaQrCodeEvento(
            dadosEvento.get("nomeEvento"), imagens.get("qrcode").file
        )

    # Valida os dados e registra o evento no bd
    dadosEvento.arteEvento = caminhoArte
    dadosEvento.arteQrcode = caminhoQrCode

    try:
        conexao = EventoBD()
        retorno = conexao.cadastrarEvento(dadosEvento.dict())
        if retorno.get("status") == "400":
            deletaImagem(dadosEvento.nomeEvento)
            return retorno
        idEvento = conexao.getEventoID(dadosEvento.nomeEvento) 
        logging.info(f"Evento cadastrado com id: {idEvento}")
        return {"mensagem": "Evento cadastrado com sucesso!", "status": "201"}
    except Exception as e:
        logging.warning("Problema para adicionar eventos.")
        return {"mensagem": str(e), "status": "400"}
