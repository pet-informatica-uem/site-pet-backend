import logging
from typing import BinaryIO
from bson.objectid import ObjectId

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

    def listarEventos(self) -> list:
        eventos: list = self.__eventoConexao.listarEventos()

        if eventos != []:
            for evento in eventos:
                evento["_id"] = str(evento["_id"])

        return eventos

    def deletarEvento(self, idEvento: str) -> bool:
        # Verifica se o evento existe
        evento: dict = self.__eventoConexao.getEvento(idEvento)

        removerEvento :bool = self.__eventoConexao.removerEvento(idEvento)

        # precisa de outra branch TODO
        deletarImagem(evento["nome evento"])
        return removerEvento

    def editarEvento(
        self, idEvento, novosDadosEvento: DadosEvento, imagens: dict
    ):
        # Verfica se o evento existe e recupera os dados dele
        dadosEventoBanco :dict = self.__eventoConexao.getEvento(idEvento)

        # Valida as imagens (se existirem)
        # TODO depende da outra branch
        if imagens["arteEvento"] and not validaImagem(imagens["arteEvento"]):
            raise ImagemInvalidaExcecao()

        if imagens["arteQrcode"] and not validaImagem(imagens["arteQrcode"]):
            raise ImagemInvalidaExcecao(message="Imagem do qrCode inválida.")

        novosDadosEvento.caminhoArteEvento = dadosEventoBanco["arte evento"]
        novosDadosEvento.caminhoArteQrcode = dadosEventoBanco["arte qrcode"]

        # Verifica os dados e atualiza o evento
        idEvento :ObjectId = self.__eventoConexao.atualizarEvento(idEvento, novosDadosEvento.paraBD())

        print('\n\n\n')
        print(idEvento)

        # Deleta as imagens antigas e armazena as novas
        if imagens["arteEvento"]:
            deletarImagem(dadosEventoBanco["nome evento"], ["eventos", "arte"])
            novosDadosEvento.caminhoArteEvento = armazenaArteEvento(
                novosDadosEvento.nomeEvento, imagens["arteEvento"]
            )  # type: ignore
        else:
            novosDadosEvento.caminhoArteEvento = dadosEventoBanco["arte evento"]

        if imagens["arteQrcode"]:
            deletarImagem(dadosEventoBanco["nome evento"], ["eventos", "qrcode"])
            novosDadosEvento.caminhoArteQrcode = armazenaQrCodeEvento(
                novosDadosEvento.nomeEvento, imagens["arteQrcode"]
            )  # type: ignore
        else:
            novosDadosEvento.caminhoArteQrcode = dadosEventoBanco["arte qrcode"]

        # Caso alguma imagem tenha sido alterada, atualiza o evento novamente para adicionar o caminho para as imagens
        if imagens["arteEvento"] or imagens["arteQrcode"]:
            self.__eventoConexao.atualizarEvento(idEvento, dadosEventoBanco)

        return idEvento


    def novoEvento(
        self, dadosEvento: DadosEvento, imagens: dict[str, BinaryIO | None]
    ) -> ObjectId:
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
        conexao = EventoBD()
        idEvento :ObjectId = conexao.cadastrarEvento(dadosEvento.paraBD())
        deletarImagem(dadosEvento.nomeEvento)
        logging.info(f"Evento cadastrado com id: {idEvento}")

        return idEvento
