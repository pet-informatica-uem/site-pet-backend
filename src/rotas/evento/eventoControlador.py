import logging
from typing import BinaryIO

from src.config import config
from src.email.operacoesEmail import emailConfirmacaoEvento
from src.img.operacoesImagem import (
    armazenaArteEvento,
    armazenaQrCodeEvento,
    deletarImagem,
    validaImagem,
)
from src.modelos.evento.evento import DadosEvento
from src.modelos.evento.eventoBD import EventoBD
from src.modelos.evento.inscritosEventoBD import InscritosEventoBD
from src.modelos.usuario.usuarioBD import UsuarioBD

from src.modelos.excecao import ImagemInvalidaExcecao, ErroInternoExcecao


class EventoControlador:
    def __init__(self):
        self.__eventoConexao = EventoBD()

    def listarEventos(self) -> dict:
        eventos: dict = self.__eventoConexao.listarEventos()

        if eventos != []:
            for evento in eventos["mensagem"]:
                evento["_id"] = str(evento["_id"])

        return eventos

    def deletarEvento(self, idEvento: str) -> bool:
        # Verifica se o evento existe
        evento: dict = self.__eventoConexao.getEvento(idEvento)

        removerEvento = self.__eventoConexao.removerEvento(idEvento)

        # precisa de outra branch TODO
        deletarImagem(evento["nome evento"])
        return removerEvento

    def editarEvento(
        self, idEvento, dadosEvento: DadosEvento, imagens: dict
    ):
        try:
            conexao = EventoBD()

            # Verfica se o evento existe e recupera os dados dele
            dadosEvento = conexao.getEvento(idEvento)

            # Valida as imagens (se existirem)
            if imagens["arteEvento"] and not validaImagem(imagens["arteEvento"]):
                raise ImagemInvalidaExcecao()

            if imagens["arteQrcode"] and not validaImagem(imagens["arteQrcode"]):
                raise ImagemInvalidaExcecao(message="Imagem do qrCode inválida.")

            dadosEvento.caminhoArteEvento = dadosEvento["arte evento"]
            dadosEvento.caminhoArteQrcode = dadosEvento["arte qrcode"]

            # Verifica os dados e atualiza o evento
            idEvento = conexao.atualizarEvento(idEvento, dadosEvento.paraBD())

            # Deleta as imagens antigas e armazena as novas
            if imagens["arteEvento"]:
                deletarImagem(dadosEvento["nome evento"], ["eventos", "arte"])
                dadosEvento.caminhoArteEvento = armazenaArteEvento(
                    dadosEvento.nomeEvento, imagens["arteEvento"]
                )  # type: ignore
            else:
                dadosEvento.caminhoArteEvento = dadosEvento["arte evento"]

            if imagens["arteQrcode"]:
                deletarImagem(dadosEvento["nome evento"], ["eventos", "qrcode"])
                dadosEvento.caminhoArteQrcode = armazenaQrCodeEvento(
                    dadosEvento.nomeEvento, imagens["arteQrcode"]
                )  # type: ignore
            else:
                dadosEvento.caminhoArteQrcode = dadosEvento["arte qrcode"]

            # Caso alguma imagem tenha sido alterada, atualiza o evento novamente para adicionar o caminho para as imagens
            if imagens["arteEvento"] or imagens["arteQrcode"]:
                conexao.atualizarEvento(idEvento, dadosEvento.paraBD())

            return idEvento

        except Exception as e:
            logging.warning("Problema para editar eventos.")
            raise Exception(e)

    def novoEvento(
        self, dadosEvento: DadosEvento, imagens: dict[str, BinaryIO | None]
    ) -> dict:
        # Valida as imagens
        if not validaImagem(imagens["arteEvento"]):  # type: ignore
            raise ImagemInvalidaExcecao(mesage="Imagem do evento inválida")

        if imagens["arteQrcode"] and not validaImagem(imagens["arteQrcode"]):
            raise ImagemInvalidaExcecao(mesage="Imagem do qrCode inválida")

        # Armazena as imagens
        caminhoArte = armazenaArteEvento(dadosEvento.nomeEvento, imagens["arteEvento"])  # type: ignore
        dadosEvento.caminhoArteEvento = caminhoArte  # type: ignore

        if imagens["arteQrcode"]:
            caminhoQrCode = armazenaQrCodeEvento(
                dadosEvento.nomeEvento, imagens["arteQrcode"]
            )
            dadosEvento.caminhoArteQrcode = caminhoQrCode  # type: ignore

        # Valida os dados e registra o evento no bd
        try:
            conexao = EventoBD()
            idEvento = conexao.cadastrarEvento(dadosEvento.paraBD())
            deletarImagem(dadosEvento.nomeEvento)
            idEvento = conexao.getEventoID(dadosEvento.nomeEvento)
            logging.info(f"Evento cadastrado com id: {idEvento}")

            return idEvento

        except Exception as e:
            logging.warning("Problema para adicionar eventos.")
            raise Exception(e)
            # raise ErroInternoExcecao()
