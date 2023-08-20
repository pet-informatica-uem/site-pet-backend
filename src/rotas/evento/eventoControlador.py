import logging
import secrets
from typing import BinaryIO

from bson.objectid import ObjectId
from fastapi import UploadFile

from modelos.evento.eventoClad import EventoAtualizar, EventoCriar
from src.config import config
from src.email.operacoesEmail import emailConfirmacaoEvento
from src.img.operacoesImagem import (
    armazenaArteEvento,
    armazenaQrCodeEvento,
    deletaImagem,
    validaImagem,
)
from src.modelos.bd import EventoBD, UsuarioBD
from src.modelos.evento.evento import Evento
from src.modelos.excecao import ErroInternoExcecao, ImagemInvalidaExcecao


class EventoControlador:
    @staticmethod
    def getEventos() -> list[Evento]:
        return EventoBD.listar()

    @staticmethod
    def getEvento(id: str) -> Evento:
        return EventoBD.buscar("_id", id)

    @staticmethod
    def deletarEvento(id: str):
        EventoControlador.getEvento(id)

        EventoBD.deletar(id)

    @staticmethod
    def editarEvento(id: str, dadosEvento: EventoAtualizar) -> Evento:
        # obtém evento
        evento: Evento = EventoControlador.getEvento(id)

        # normaliza dados
        dadosEvento.titulo = dadosEvento.titulo.strip()
        dadosEvento.descricao = dadosEvento.descricao.strip()
        dadosEvento.local = dadosEvento.local.strip()

        # atualiza dados
        d = evento.model_dump(by_alias=True)
        d.update(dadosEvento.model_dump(exclude_none=True))
        evento = Evento(**d)  # type: ignore

        EventoBD.atualizar(evento)

        return evento

    @staticmethod
    def atualizarImagensEvento(
        id: str, arte: UploadFile | None, cracha: UploadFile | None
    ):
        # obtém evento
        evento: Evento = EventoControlador.getEvento(id)

        if arte:
            if not validaImagem(arte.file):
                raise ImagemInvalidaExcecao()

            deletaImagem(evento.titulo, ["eventos", "arte"])
            caminhoArte: str = armazenaArteEvento(evento.titulo, arte.file)  # type: ignore
            evento.arte = caminhoArte  # type: ignore

            # atualiza no bd
            EventoBD.atualizar(evento)

        if cracha:
            if not validaImagem(cracha.file):
                raise ImagemInvalidaExcecao()

            deletaImagem(evento.titulo, ["eventos", "cracha"])
            caminhoCracha: str = armazenaQrCodeEvento(evento.titulo, cracha.file)  # type: ignore
            evento.cracha = caminhoCracha  # type: ignore

            # atualiza no bd
            EventoBD.atualizar(evento)

    @staticmethod
    def cadastrarEvento(dadosEvento: EventoCriar):
        """
        Cria uma conta com os dados fornecidos, e envia um email
        de confirmação de criação de conta ao endereço fornecido.

        A criação da conta pode não suceder por erro na validação de dados,
        por já haver uma conta cadastrada com tal CPF ou email ou por falha
        de conexão com o banco de dados.
        """

        # normaliza dados
        dadosEvento.titulo = dadosEvento.titulo.strip()
        dadosEvento.descricao = dadosEvento.descricao.strip()
        dadosEvento.local = dadosEvento.local.strip()

        # cria evento
        evento: Evento = Evento(
            **dadosEvento.model_dump(),
            _id=secrets.token_hex(16),
            vagasDisponiveisComNote=dadosEvento.vagasComNote,
            vagasDisponiveisSemNote=dadosEvento.vagasSemNote
        )
        EventoBD.criar(evento)

        return evento.id
