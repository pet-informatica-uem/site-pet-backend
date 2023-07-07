import logging

from app.model import EventoBD
from app.model.evento import DadosEvento
from core.operacoesImagem import (
    armazenaArteEvento,
    armazenaQrCodeEvento,
    deletaImagem,
    validaImagem,
)


def controladorNovoEvento(dadosEvento: DadosEvento, imagens: dict) -> dict:
    # Valida as imagens
    if not validaImagem(imagens["arteEvento"]):
        return {"mensagem": "Arte do evento inválida.", "status": "400"}

    if imagens["arteQrcode"] and not validaImagem(imagens["arteQrcode"]):
        return {"mensagem": "Imagem do qrCode inválida.", "status": "400"}

    # Armazena as imagens
    caminhoArte = armazenaArteEvento(dadosEvento.nomeEvento, imagens["arteEvento"])
    dadosEvento.caminhoArteEvento = caminhoArte

    if imagens["arteQrcode"]:
        caminhoQrCode = armazenaQrCodeEvento(
            dadosEvento.nomeEvento, imagens["arteQrcode"]
        )
        dadosEvento.caminhoArteQrcode = caminhoQrCode

    # Valida os dados e registra o evento no bd
    try:
        conexao = EventoBD()
        retorno = conexao.cadastrarEvento(dadosEvento.paraBD())
        if retorno["status"] != "200":
            deletaImagem(dadosEvento.nomeEvento)
            return retorno
        idEvento = conexao.getEventoID(dadosEvento.nomeEvento)
        logging.info(f"Evento cadastrado com id: {idEvento}")

        return {"mensagem": "Evento cadastrado com sucesso!", "status": "201"}

    except Exception as e:
        logging.warning("Problema para adicionar eventos.")
        return {"mensagem": "Problema interno.", "status": "400"}


def controladorEditarEvento(idEvento, dadosEvento: DadosEvento, imagens: dict):
    try:
        conexao = EventoBD()

        # Verfica se o evento existe e recupera os dados dele
        eventoOld = conexao.getEvento(idEvento)
        if eventoOld["status"] == "404":
            return {"mensagem": "Evento não encontrado!", "status": "404"}
        dadosEventoOld = eventoOld["mensagem"]

        # Valida as imagens (se existirem)
        if imagens["arteEvento"] and not validaImagem(imagens["arteEvento"]):
            return {"mensagem": "Arte do evento inválida.", "status": "400"}

        if imagens["arteQrcode"] and not validaImagem(imagens["arteQrcode"]):
            return {"mensagem": "Imagem do qrCode inválida.", "status": "400"}

        dadosEvento.caminhoArteEvento = dadosEventoOld["arte evento"]
        dadosEvento.caminhoArteQrcode = dadosEventoOld["arte qrcode"]

        # Verifica os dados e atualiza o evento
        retorno = conexao.atualizarEvento(idEvento, dadosEvento.paraBD())

        if retorno["status"] != "200":
            return {"mensagem": retorno["mensagem"], "status": retorno["status"]}

        # Deleta as imagens antigas e armazena as novas
        if imagens["arteEvento"]:
            deletaImagem(dadosEventoOld["nome evento"], ["eventos", "arte"])
            dadosEvento.caminhoArteEvento = armazenaArteEvento(
                dadosEvento.nomeEvento, imagens["arteEvento"]
            )
        else:
            dadosEvento.caminhoArteEvento = dadosEventoOld["arte evento"]

        if imagens["arteQrcode"]:
            deletaImagem(dadosEventoOld["nome evento"], ["eventos", "qrcode"])
            dadosEvento.caminhoArteQrcode = armazenaQrCodeEvento(
                dadosEvento.nomeEvento, imagens["arteQrcode"]
            )
        else:
            dadosEvento.caminhoArteQrcode = dadosEventoOld["arte qrcode"]

        # Caso alguma imagem tenha sido alterada, atualiza o evento novamente para adicionar o caminho para as imagens
        if imagens["arteEvento"] or imagens["arteQrcode"]:
            conexao.atualizarEvento(idEvento, dadosEvento.paraBD())

        return {"mensagem": "Evento atualizado com sucesso!", "status": "200"}

    except Exception as e:
        logging.warning("Problema para editar eventos.")
        return {"mensagem": str(e), "status": "500"}


class EventoController:
    def __init__(self):
        self.__evento = EventoBD()

    def listarEventos(self) -> dict:
        eventos: dict = self.__evento.listarEventos()

        if eventos["status"] == "404":
            return eventos

        for evento in eventos["mensagem"]:
            evento["_id"] = str(evento["_id"])

        return eventos
