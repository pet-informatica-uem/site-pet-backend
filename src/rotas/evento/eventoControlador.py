import logging
import secrets
from typing import BinaryIO

from bson.objectid import ObjectId
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
from src.modelos.evento.eventoQuery import eventoQuery
from src.modelos.excecao import (
    APIExcecaoBase,
    ImagemInvalidaExcecao,
    ImagemNaoSalvaExcecao,
)


#Inscritos:
from src.modelos.evento.eventoClad import (
    InscritoAtualizar,
    InscritoCriar,
    InscritoDeletar,
    InscritoLer
)

from src.modelos.evento.evento import TipoVaga
import logging
from datetime import datetime
from fastapi import BackgroundTasks, UploadFile
from PIL import Image

from src.config import config
from src.email.operacoesEmail import enviarEmailConfirmacaoEvento
from src.img.operacoesImagem import armazenaComprovante, deletaImagem, validaComprovante
from src.modelos.bd import EventoBD, InscritoBD, UsuarioBD, cliente
from src.modelos.evento.evento import Evento
from src.modelos.excecao import APIExcecaoBase
from src.modelos.usuario.usuario import Usuario



class EventoControlador:
    @staticmethod
    def getEventos(query: eventoQuery) -> list[Evento]:
        return EventoBD.listar(query)

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
            inicioEvento=dadosEvento.dias[0][0],
            fimEvento=dadosEvento.dias[-1][1],
        )
        EventoBD.criar(evento)

        # cria pastas evento
        criaPastaEvento(evento.id)

        return evento.id


    #PARTE DE INSCRITOS

    @staticmethod
    def cadastrarInscrito(
        idEvento: str,
        idUsuario: str,
        dadosInscrito: InscritoCriar,
        comprovante: UploadFile | None,
        tasks: BackgroundTasks,
    ):
        # Recupera o evento
        evento: Evento = EventoControlador.getEvento(idEvento)

        # Verifica se está no período de inscrição
        if (
            evento.inicioInscricao > datetime.now()
            and evento.fimInscricao < datetime.now()
        ):
            raise APIExcecaoBase(message="Fora do período de inscrição")

        # Verifica se há vagas disponíveis
        if dadosInscrito.tipoVaga == TipoVaga.COM_NOTE:
            if evento.vagasDisponiveisComNote == 0:
                raise APIExcecaoBase(message="Não há vagas disponíveis com note")
        else:
            if evento.vagasDisponiveisSemNote == 0:
                raise APIExcecaoBase(message="Não há vagas disponíveis sem note")

        if evento.valor != 0:
            if comprovante:
                if not validaComprovante(comprovante.file):
                    raise APIExcecaoBase(message="Comprovante inválido.")

                deletaImagem(idUsuario, ["eventos", evento.id, "comprovantes"])
                caminhoComprovante = armazenaComprovante(
                    evento.id, idUsuario, comprovante.file
                )
            else:
                raise APIExcecaoBase(
                    message="Comprovante obrigatório para eventos pagos."
                )
        else:
            caminhoComprovante = None

        dictInscrito = {
            "idUsuario": idUsuario,
            #"tipovaga": None,
            #"nivelConhecimento": None,
            #"comprovante": comprovante,
            "dataInscricao": datetime.now(),
        }

        dictInscrito.update(**dadosInscrito.model_dump())
        dictInscrito.comprovante = str(caminhoComprovante) if caminhoComprovante else None  # type: ignore

        if dictInscrito.tipoVaga == TipoVaga.COM_NOTE:
            evento.vagasDisponiveisComNote -= 1
        else:
            evento.vagasDisponiveisSemNote -= 1

        # Recupera o usuário
        usuario: Usuario = UsuarioBD.buscar("_id", idUsuario)

        # Adiciona o evento na lista de eventos inscritos do usuário
        usuario.eventosInscrito.append(idEvento)

        # Realiza as operações no BD usando uma transação
        session = cliente.start_session()
        try:
            session.start_transaction()

            EventoBD.criarInscrito(idEvento,dictInscrito) 
            EventoBD.atualizar(evento)
            UsuarioBD.atualizar(usuario)

            # Commita a transação se der tudo certo
            session.commit_transaction()
            session.end_session()

        # Aborta a transação caso ocorra algum erro
        except Exception as e:
            logging.error(
                f"Erro ao inscrever usuário em {evento.titulo}. Erro: {str(e)}"
            )

            session.abort_transaction()
            session.end_session()
            raise APIExcecaoBase(message="Erro ao criar inscrito")

        # Envia email de confirmação de inscrição
        #tasks.add_task(
        #    enviarEmailConfirmacaoEvento,
        #    usuario.email,
        #    evento.id,
        #    dadosInscrito.tipoVaga,
        #)




