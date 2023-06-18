from core.operacoesImagem import (
    armazenaArteEvento,
    armazenaQrCodeEvento,
    deletaImagem,
)
from app.models import EventoBD
from app.models.evento import DadosEvento

from fastapi import UploadFile

import logging


def controladorNovoEvento(
    dadosEvento: DadosEvento, imagens: dict[str, UploadFile] | None
) -> dict:
    # Valida e armazena as imagens
    caminhoArte = armazenaArteEvento(dadosEvento.nomeEvento, imagens.get("arte").file)
    if caminhoArte:
        dadosEvento.arteEvento = caminhoArte
    else:
        return {"mensagem": "Arte do evento inválida.", "status": "400"}

    if imagens.get("qrcode"):
        caminhoQrCode = armazenaQrCodeEvento(
            dadosEvento.nomeEvento, imagens.get("qrcode").file
        )
        if caminhoQrCode:
            dadosEvento.arteQrcode = caminhoQrCode
        else:
            deletaImagem(dadosEvento.nomeEvento)
            return {"mensagem": "Arte do qrcode inválida.", "status": "400"}

    # Valida os dados e registra o evento no bd
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
