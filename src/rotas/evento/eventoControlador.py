import logging
import secrets
from typing import BinaryIO
from bson.objectid import ObjectId
from fastapi import UploadFile

# Importações dos módulos internos
from src.config import config
from src.img.criaPastas import criaPastaEvento
from src.img.operacoesImagem import (
    armazenaArteEvento,
    armazenaCrachaEvento,
    deletaImagem,
    validaImagem,
)
from src.modelos.bd import EventoBD, InscritoBD
from src.modelos.evento.evento import Evento
from src.modelos.evento.eventoClad import EventoAtualizar, EventoCriar
from src.modelos.evento.intervaloBusca import IntervaloBusca
from src.modelos.excecao import (
    APIExcecaoBase,
    ImagemInvalidaExcecao,
    ImagemNaoSalvaExcecao,
)
from src.modelos.inscrito.inscrito import Inscrito


class EventoControlador:
    """
    Classe controlador para gerenciar operações sobre eventos, incluindo
    criação, atualização, remoção e manipulação de dados e imagens.
    """
     
    @staticmethod
    def getEventos(query: IntervaloBusca) -> list[Evento]:
        """
        Lista todos os eventos de acordo com os parâmetros de busca.

        Parâmetros:
            query (IntervaloBusca): Objeto contendo os parâmetros de busca para filtrar eventos.

        Retorno:
            list[Evento]: Lista de eventos que correspondem aos filtros aplicados.
        """
        return EventoBD.listar(query)

    @staticmethod
    def getEvento(id: str) -> Evento:
        """
        Recupera um evento específico pelo seu ID.

        Parâmetros:
            id (str): Identificador único do evento.

        Retorno:
            Evento: Instância do evento encontrado.
        """
        return EventoBD.buscar("_id", id)

    @staticmethod
    def deletarEvento(id: str):
        """
        Deleta um evento do banco de dados.

        Parâmetros:
            id (str): Identificador único do evento a ser deletado.
        """
        EventoControlador.getEvento(id)

        EventoBD.deletar(id)

    @staticmethod
    def editarEvento(id: str, dadosEvento: EventoAtualizar) -> Evento:
        """
        Edita um evento existente com base nos novos dados fornecidos.

        Parâmetros:
            id (str): Identificador do evento a ser atualizado.
            dadosEvento (EventoAtualizar): Objeto com dados atualizados do evento.

        Retorno:
            Evento: Evento atualizado.

        Exceções:
            APIExcecaoBase: Lançada se o número de vagas especificado é inferior ao número de inscritos existentes.
        """
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
        """
        Atualiza as imagens de arte e crachá associadas ao evento.

        Parâmetros:
            id (str): Identificador do evento.
            arte (UploadFile | None): Imagem opcional para a arte do evento.
            cracha (UploadFile | None): Imagem opcional para o crachá do evento.

        Exceções:
            ImagemInvalidaExcecao: Lançada se a imagem fornecida for inválida.
            ImagemNaoSalvaExcecao: Lançada se houver erro ao salvar a imagem.
        """
        # obtém evento
        evento: Evento = EventoControlador.getEvento(id)

        if arte:
            if not validaImagem(arte.file):
                raise ImagemInvalidaExcecao()

            deletaImagem(evento.id, ["eventos", evento.id, "arte"])

            caminhoArte = armazenaArteEvento(evento.id, arte.file)

            if not caminhoArte:
                raise ImagemNaoSalvaExcecao()

            evento.arte = str(caminhoArte)

            # atualiza no bd
            EventoBD.atualizar(evento)

        if cracha:
            if not validaImagem(cracha.file):
                raise ImagemInvalidaExcecao()

            deletaImagem(evento.id, ["eventos", evento.id, "cracha"])
            caminhoCracha = armazenaCrachaEvento(evento.id, cracha.file)

            if not caminhoCracha:
                raise ImagemNaoSalvaExcecao()

            evento.cracha = str(caminhoCracha)

            # atualiza no bd
            EventoBD.atualizar(evento)

    @staticmethod
    def cadastrarEvento(dadosEvento: EventoCriar):
        """
        Cadastra um novo evento e cria a estrutura de diretórios associada.

        Parâmetros:
            dadosEvento (EventoCriar): Objeto com os dados do evento a ser criado.

        Retorno:
            str: ID do evento recém-criado.
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
            inicioEvento=dadosEvento.dias[0][0],
            fimEvento=dadosEvento.dias[-1][1],
        )
        EventoBD.criar(evento)

        # cria pastas evento
        criaPastaEvento(evento.id)

        return evento.id
