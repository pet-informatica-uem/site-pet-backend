import logging
import secrets

from fastapi import UploadFile

from src.config import config
from src.img.criaPastas import criaPastaEvento
from src.img.operacoesImagem import (
    armazenaArteEvento,
    armazenaCrachaEvento,
    deletaImagem,
    validaImagem,
)
from src.modelos.bd import EventoBD
from src.modelos.evento.evento import Evento
from src.modelos.evento.eventoClad import EventoAtualizar, EventoCriar
from src.modelos.excecao import APIExcecaoBase, ImagemInvalidaExcecao


class EventoControlador(EventoBD):
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
        eventoOld: Evento = EventoControlador.getEvento(id)

        qtdInscritosNote: int = (
            eventoOld.vagasComNote - eventoOld.vagasDisponiveisComNote
        )
        qtdInscritosSemNote: int = (
            eventoOld.vagasSemNote - eventoOld.vagasDisponiveisSemNote
        )

        if (
            dadosEvento.vagasComNote != None
            and dadosEvento.vagasComNote < qtdInscritosNote
        ):
            raise APIExcecaoBase(
                message="Erro ao alterar vagas com note: numero de inscritos superior ao total de vagas com note."
            )

        if (
            dadosEvento.vagasSemNote != None
            and dadosEvento.vagasSemNote < qtdInscritosSemNote
        ):
            raise APIExcecaoBase(
                message="Erro ao alterar vagas sem note: numero de inscritos superior ao total de vagas sem note."
            )

        # normaliza dados
        if dadosEvento.titulo:
            dadosEvento.titulo = dadosEvento.titulo.strip()
        if dadosEvento.descricao:
            dadosEvento.descricao = dadosEvento.descricao.strip()
        if dadosEvento.local:
            dadosEvento.local = dadosEvento.local.strip()

        # atualiza dados
        d = eventoOld.model_dump(by_alias=True)
        if dadosEvento.vagasComNote:
            d.update(
                vagasDisponiveisComNote=dadosEvento.vagasComNote - qtdInscritosNote
            )

        if dadosEvento.vagasSemNote:
            d.update(
                vagasDisponiveisSemNote=dadosEvento.vagasSemNote - qtdInscritosSemNote
            )

        d.update(dadosEvento.model_dump(exclude_none=True))
        evento = Evento(**d)

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

            deletaImagem(evento.id, ["eventos", evento.id, "arte"])
            caminhoArte: str | None = armazenaArteEvento(evento.id, arte.file)
            evento.imagemCapa = caminhoArte

            # atualiza no bd
            EventoBD.atualizar(evento)

        if cracha:
            if not validaImagem(cracha.file):
                raise ImagemInvalidaExcecao()

            deletaImagem(evento.id, ["eventos", evento.id, "cracha"])
            caminhoCracha: str | None = armazenaCrachaEvento(evento.id, cracha.file)
            evento.imagemCracha = caminhoCracha

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
            vagasDisponiveisSemNote=dadosEvento.vagasSemNote,
            fimEvento=dadosEvento.dias[-1][1],
        )
        EventoBD.criar(evento)

        # cria pastas evento
        criaPastaEvento(evento.id)

        return evento.id
