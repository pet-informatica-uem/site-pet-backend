from core.operacoesImagem import (
    armazenaArteEvento,
    armazenaQrCodeEvento,
    deletaImagem,
    validaImagem,
)
from app.model import EventoBD
from app.model.evento import DadosEvento

from fastapi import UploadFile

import logging


def controladorNovoEvento(
    dadosEvento: DadosEvento, imagens: dict[str, UploadFile] | None
) -> dict:
    # Valida as imagens
    if not validaImagem(imagens["arte"].file):
        return {"mensagem": "Arte do evento inválida.", "status": "400"}

    if imagens.get("qrCode") and not validaImagem(imagens["qrCode"].file):
        return {"mensagem": "Imagem do qrCode inválida.", "status": "400"}

    # Armazena as imagens
    caminhoArte = armazenaArteEvento(dadosEvento.nomeEvento, imagens.get("arte").file)
    print(caminhoArte)
    dadosEvento.arteEvento = caminhoArte

    if imagens.get("qrcode"):
        caminhoQrCode = armazenaQrCodeEvento(
            dadosEvento.nomeEvento, imagens.get("qrcode").file
        )
        dadosEvento.arteQrcode = caminhoQrCode

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
        return {"mensagem": "Problema interno.", "status": "400"}


def controladorEditarEvento(evento, dadosEvento: DadosEvento, imagens: dict):
    try:
        conexao = EventoBD()

        # Verfica se o evento existe e recupera os dados dele
        eventoOld = conexao.getEvento(dadosEvento.nomeEvento)
        if eventoOld["status"] == "404":
            return {"mensagem": "Evento não encontrado!", "status": "404"}
        dadosEventoOld = eventoOld["mensagem"]

        # Valida as imagens (se existirem)
        if imagens.get("arte") and not validaImagem(imagens["arte"].file):
            return {"mensagem": "Arte do evento inválida.", "status": "400"}

        if imagens.get("qrCode") and not validaImagem(imagens["qrCode"].file):
            return {"mensagem": "Imagem do qrCode inválida.", "status": "400"}

        # Verifica os dados e atualiza o evento
        retorno = conexao.atualizarEvento(evento, dadosEvento.dict())

        if retorno["status"] != "200":
            return {"mensagem": retorno["mensagem"], "status": retorno["status"]}

        # Deleta as imagens antigas e armazena as novas
        if imagens.get("arte"):
            deletaImagem(dadosEvento.nomeEvento, "evento/arte/")
            dadosEvento.arteEvento = (dadosEvento.nomeEvento, imagens["arte"].file)
        else:
            dadosEvento.arteEvento = dadosEventoOld["arte evento"]

        if imagens.get("qrCode"):
            deletaImagem(dadosEvento.nomeEvento, "evento/qrCode/")
            dadosEvento.arteQrcode = (dadosEvento.nomeEvento, imagens["qrCode"].file)
        else:
            dadosEvento.arteQrcode = dadosEventoOld["arte qrcode"]

        # Caso alguma imagem tenha sido alterada, atualiza o evento novamente para adicionar o caminho para as imagens
        if dadosEvento.arteEvento or dadosEvento.arteQrcode:
            conexao.atualizarEvento(dadosEvento.nomeEvento, dadosEvento.dict())

        return {"mensagem": "Evento atualizado com sucesso!", "status": "200"}

    except Exception as e:
        logging.warning("Problema para editar eventos.")
        return {"mensagem": str(e), "status": "500"}
