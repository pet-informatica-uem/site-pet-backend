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
from src.modelos.bd import EventoBD, UsuarioBD, cliente
from src.modelos.evento.evento import Evento, Inscrito, TipoVaga
from src.modelos.evento.eventoClad import (
    EventoAtualizar,
    EventoCriar,
    InscritoAtualizar,
    InscritoCriar,
    InscritoDeletar,
)
from src.modelos.evento.intervaloBusca import IntervaloBusca
from src.modelos.excecao import (
    APIExcecaoBase,
    ForaDoPeriodoDeInscricaoExcecao,
    ImagemInvalidaExcecao,
    ImagemNaoSalvaExcecao,
    SemVagasDisponiveisExcecao,
    NaoEncontradoExcecao,
)

from src.modelos.usuario.usuario import Usuario

# Imports adicionais para envio de email e manipulação de imagens
import logging
from datetime import datetime
from fastapi import BackgroundTasks, UploadFile
from PIL import Image

from src.config import config
from src.email.operacoesEmail import enviarEmailConfirmacaoEvento
from src.img.operacoesImagem import armazenaComprovante, deletaImagem, validaComprovante
from src.modelos.excecao import APIExcecaoBase
from src.modelos.usuario.usuario import Usuario


class EventoControlador:
    """
    Classe controladora para gerenciar operações sobre eventos, incluindo
    criação, atualização, remoção e manipulação de dados e imagens.
    """
     
    @staticmethod
    def getEventos(query: IntervaloBusca) -> list[Evento]:
        """
        Lista todos os eventos de acordo com os parâmetros de busca.

        :param query: Objeto contendo os parâmetros de busca para filtrar eventos.

        :return eventos: Lista de eventos que correspondem aos filtros aplicados.
        """
        return EventoBD.listar(query)

    @staticmethod
    def getEvento(id: str) -> Evento:
        """
        Recupera um evento específico pelo seu ID.

        :param id: Identificador único do evento.

        :return evento: Instância do evento encontrado.

        :raises NaoEncontradoExcecao: Lançada se o evento com o ID especificado não for encontrado.
        """
        return EventoBD.buscar("_id", id)

    @staticmethod
    def deletarEvento(id: str):
        """
        Deleta um evento do banco de dados.

        :param id: Identificador único do evento a ser deletado.

        :raises NaoEncontradoExcecao: Lançada se o evento com o ID especificado não for encontrado.
        """
        EventoControlador.getEvento(id)
        EventoBD.deletar(id)

    @staticmethod
    def editarEvento(id: str, dadosEvento: EventoAtualizar) -> Evento:
        """
        Edita um evento existente com base nos novos dados fornecidos.

        :param id: Identificador do evento a ser atualizado.
        :param dadosEvento: Objeto com dados atualizados do evento.

        :return Evento: Evento atualizado.

        :raises NaoEncontradoExcecao: Lançada se o evento com o ID especificado não for encontrado.
        :raises SemVagasDisponiveisExcecao: Lançada se o número de vagas especificado é inferior ao número de inscritos existentes.
        """
        # Obtém evento
        eventoOld: Evento = EventoControlador.getEvento(id)


        qtdInscritosNote: int = (
            eventoOld.vagasComNote - eventoOld.vagasDisponiveisComNote
        )

        qtdInscritosSemNote: int = (
            eventoOld.vagasSemNote - eventoOld.vagasDisponiveisSemNote
        )

        if (
            dadosEvento.vagasComNote is not None
            and dadosEvento.vagasComNote < qtdInscritosNote
        ):
            raise APIExcecaoBase(
                message="Erro ao alterar vagas com note: numero de inscritos superior ao total de vagas com note."
            )

        if (
            dadosEvento.vagasSemNote is not None
            and dadosEvento.vagasSemNote < qtdInscritosSemNote
        ):
            raise APIExcecaoBase(
                message="Erro ao alterar vagas sem note: numero de inscritos superior ao total de vagas sem note."
            )

        # Normaliza dados
        if dadosEvento.titulo:
            dadosEvento.titulo = dadosEvento.titulo.strip()
        if dadosEvento.descricao:
            dadosEvento.descricao = dadosEvento.descricao.strip()
        if dadosEvento.local:
            dadosEvento.local = dadosEvento.local.strip()

        # Atualiza dados
        d = eventoOld.model_dump(by_alias=True)
        if dadosEvento.vagasComNote is not None:
            d.update(
                vagasDisponiveisComNote=dadosEvento.vagasComNote - qtdInscritosNote
            )

        if dadosEvento.vagasSemNote is not None:
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

        :param id: Identificador do evento.
        :param arte: Imagem opcional para a arte do evento.
        :param cracha: Imagem opcional para o crachá do evento.

        :raises NaoEncontradoExcecao: Lançada se o evento com o ID especificado não for encontrado.
        :raises ImagemInvalidaExcecao: Lançada se a imagem fornecida for inválida.
        :raises ImagemNaoSalvaExcecao: Lançada se houver erro ao salvar a imagem.
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

        :param dadosEvento: Objeto com os dados do evento a ser criado.

        :return str: ID do evento recém-criado.

        :raises JaExisteExcecao: Lançada se já existir um evento com o mesmo título.
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

    @staticmethod
    def cadastrarInscrito(
        idEvento: str,
        idUsuario: str,
        dadosInscrito: InscritoCriar,
        comprovante: UploadFile | None,
        tasks: BackgroundTasks,
    ):
        """
        Cadastra um inscrito em um evento.

        :param idEvento: identificador único do evento.
        :param idUsuario: identificador único do usuário que será inscrito.
        :param dadosInscrito: informações do inscrito a ser cadastrado.
        :param comprovante: comprovante de pagamento, no caso do evento ser pago.
        :param tasks: gerenciador de tarefas.
        
        :raises ForaDoPeriodoDeInscricaoExcecao: Se estiver fora do período de inscrição.
        :raises SemVagasDisponiveisExcecao: Se não houver vagas disponíveis.
        :raises ComprovanteInvalido: Se o comprovante enviado for inválido.
        :raises ComprovanteObrigatorioExcecao: Se o evento for pago e não for enviado comprovante.
        :raises APIExcecaoBase: Se houver problema no BD.
        """
        # Recupera o evento
        evento: Evento = EventoControlador.getEvento(idEvento)

        # Verifica se está no período de inscrição
        if (
            evento.inicioInscricao > datetime.now()
            or evento.fimInscricao < datetime.now()
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
            "tipoVaga": dadosInscrito.tipoVaga,
            "nivelConhecimento": dadosInscrito.nivelConhecimento,
            "comprovante": comprovante,
            "dataInscricao": datetime.now()
        }

        # dictInscrito.update(**dadosInscrito.model_dump())
        dictInscrito["comprovante"] = (
            str(caminhoComprovante) if caminhoComprovante else None
        )

        inscrito = Inscrito(**dictInscrito)

        if inscrito.tipoVaga == TipoVaga.COM_NOTE:
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
            
            EventoBD.criarInscrito(idEvento, inscrito)
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
        '''
        tasks.add_task(
            enviarEmailConfirmacaoEvento,
            usuario.email,
            evento.id,
            dadosInscrito.tipoVaga,
        )
        '''

    # Métodos adicionados do InscritosControlador
    @staticmethod
    def getInscritos(idEvento: str) -> list[Inscrito]:
        """
        Recupera os inscritos de um evento.

        :param idEvento: Identificador único do evento.

        :return: Lista de inscritos do evento.
        """
        return EventoBD.listarInscritosEvento(idEvento)

    @staticmethod
    def getInscrito(idEvento: str, idUsuario: str) -> Inscrito:
        """
        Recupera um inscrito em um evento.

        :param idEvento: Identificador único do evento.
        :param idUsuario: Identificador único do usuário.

        :return: Inscrição do inscrito no evento.
        """
        return EventoBD.buscarInscrito(idEvento, idUsuario)

    @staticmethod
    def editarInscrito(idEvento: str, idUsuario: str, inscritoAtualizar: InscritoAtualizar):
        """
        Edita o tipo de vaga de um inscrito em um evento.
        
        :param idEvento: Identificador único do evento.
        :param idUsuário: Identificador único do usuário a ser editado.
        :param inscritoAtualizar: Tipo de vaga atual do inscrito a ser editado.
        
        :raises SemVagasDisponiveisExcecao: Se não houver vaga disponível no novo tipo.
        """
        # Recupera o evento e o inscrito
        evento = EventoControlador.getEvento(idEvento)
        inscrito = EventoBD.buscarInscrito(idEvento, idUsuario)

        # Atualiza o tipo de vaga se necessário
        if inscritoAtualizar.tipoVaga and inscritoAtualizar.tipoVaga != inscrito.tipoVaga:
            # Verifica disponibilidade e atualiza vagas
            if inscritoAtualizar.tipoVaga == TipoVaga.COM_NOTE:
                if evento.vagasDisponiveisComNote <= 0:
                    raise SemVagasDisponiveisExcecao()
                evento.vagasDisponiveisComNote -= 1
                evento.vagasDisponiveisSemNote += 1
            else:
                if evento.vagasDisponiveisSemNote <= 0:
                    raise SemVagasDisponiveisExcecao()
                evento.vagasDisponiveisSemNote -= 1
                evento.vagasDisponiveisComNote += 1
            inscrito.tipoVaga = inscritoAtualizar.tipoVaga

        # Atualiza o inscrito na lista de inscritos do evento
        for idx, inscrito_item in enumerate(evento.inscritos):
            if inscrito_item.idUsuario == idUsuario:
                evento.inscritos[idx] = inscrito
                break

        # Atualiza o evento no banco de dados
        EventoBD.atualizar(evento)

    @staticmethod
    def removerInscrito(idEvento: str, idUsuario: str):
        """
        Remove um inscrito de um evento.

        :param idEvento: Identificador único do evento.
        :param idUsuario: Dados do usuário a ser removido.
        
        :raises NaoEncontradoExcecao: Se o inscrito não for encontrado no evento.
        """
        # Recupera o evento
        evento: Evento = EventoControlador.getEvento(idEvento)

        # Remove o inscrito da lista
        inscrito_to_remove = None
        for inscrito in evento.inscritos:
            if inscrito.idUsuario == idUsuario:
                inscrito_to_remove = inscrito
                break
        if not inscrito_to_remove:
            raise NaoEncontradoExcecao(message="Inscrito não encontrado no evento.")
        
        evento.inscritos.remove(inscrito_to_remove)

        # Ajusta vagas disponíveis
        if inscrito_to_remove.tipoVaga == TipoVaga.COM_NOTE:
            evento.vagasDisponiveisComNote += 1
        else:
            evento.vagasDisponiveisSemNote += 1

        # Atualiza o evento no banco de dados
        EventoBD.atualizar(evento)

        # Atualiza a lista de eventos inscritos do usuário
        usuario = UsuarioBD.buscar("_id", idUsuario)
        if idEvento in usuario.eventosInscrito:
            usuario.eventosInscrito.remove(idEvento)
            UsuarioBD.atualizar(usuario)