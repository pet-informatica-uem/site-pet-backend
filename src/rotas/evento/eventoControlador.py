import logging
import secrets
from typing import BinaryIO
from pathlib import Path
from bson.objectid import ObjectId
from fastapi import File, UploadFile

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
    EventoAtualizarAdmin,
    EventoCriar,
    InscritoAtualizar,
    InscritoCriar,
    InscritoLer,
)
from src.modelos.evento.intervaloBusca import IntervaloBusca
from src.modelos.excecao import (
    ComprovanteInvalido,
    ComprovanteObrigatorioExcecao,
    ErroInternoExcecao,
    ErroNaAlteracaoExcecao,
    ForaDoPeriodoDeInscricaoExcecao,
    ImagemInvalidaExcecao,
    ImagemNaoSalvaExcecao,
    JaExisteExcecao,
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
from src.email.operacoesEmail import (
    enviarEmailConfirmacaoEvento,
    enviarEmailGenerico,
    enviarEmailComAnexos,
)
from src.img.operacoesImagem import armazenaComprovante, deletaImagem, validaComprovante
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
    def editarEvento(id: str, dadosEvento: EventoAtualizarAdmin) -> Evento:
        """
        Edita um evento existente com base nos novos dados fornecidos.

        :param id: Identificador do evento a ser atualizado.
        :param dadosEvento: Objeto com dados atualizados do evento.

        :return Evento: Evento atualizado.

        :raises NaoEncontradoExcecao: Lançada se o evento com o ID especificado não for encontrado.
        :raises ErroNaAlteracaoExcecao: Lançada se o número de vagas especificado é inferior ao número de inscritos existentes.
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
            raise ErroNaAlteracaoExcecao(
                message="Erro ao alterar vagas com note: numero de inscritos superior ao total de vagas com note."
            )

        if (
            dadosEvento.vagasSemNote is not None
            and dadosEvento.vagasSemNote < qtdInscritosSemNote
        ):
            raise ErroNaAlteracaoExcecao(
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

        # Recalcula as datas caso os dias do evento tenham sido alterados
        if dadosEvento.dias is not None:
            d.update(
                inicioEvento=dadosEvento.dias[0][0],
                fimEvento=dadosEvento.dias[-1][1],
            )

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

        return evento

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
        
        :raises ForaDoPeriodoDeInscricaoExcecao: Caso não esteja no período de inscrição.
        :raises SemVagasDisponiveisExcecao: Se não houver vagas disponíveis.
        :raises ComprovanteInvalido: Se o comprovante enviado for inválido.
        :raises ComprovanteObrigatorioExcecao: Se o evento for pago e não for enviado comprovante.
        :raises ErroInternoExcecao: Se houver problema no Banco de Dados.
        """
        # Recupera o evento
        evento: Evento = EventoControlador.getEvento(idEvento)

        # Valida a duplicidade antes de substituir ou armazenar o comprovante.
        if EventoBD.verificarInscricaoExistente(idEvento, idUsuario):
            raise JaExisteExcecao(message="Usuário já está inscrito neste evento.")

        # Verifica se está no período de inscrição
        if (
            evento.inicioInscricao > datetime.now()
            or evento.fimInscricao < datetime.now()
        ):
            raise ForaDoPeriodoDeInscricaoExcecao(message="Fora do período de inscrição")

        caminhoComprovante = None
        if evento.valor != 0:
            if not comprovante:
                raise ComprovanteObrigatorioExcecao(
                    message="Comprovante obrigatório para eventos pagos."
                )
            if not validaComprovante(comprovante.file):
                raise ComprovanteInvalido(message="Comprovante inválido.")
            comprovante.file.seek(0)
            caminhoComprovante = armazenaComprovante(
                evento.id, idUsuario, comprovante.file
            )
            if not caminhoComprovante:
                raise ImagemNaoSalvaExcecao()

        inscrito = Inscrito(
            idUsuario=idUsuario,
            tipoVaga=dadosInscrito.tipoVaga,
            nivelConhecimento=dadosInscrito.nivelConhecimento,
            comprovante=str(caminhoComprovante) if caminhoComprovante else None,
            statusComprovante="pendente" if caminhoComprovante else None,
            dataInscricao=datetime.now(),
        )
        usuario: Usuario = UsuarioBD.buscar("_id", idUsuario)
        try:
            EventoBD.criarInscrito(idEvento, inscrito)
            try:
                UsuarioBD.adicionarEventoInscrito(idUsuario, idEvento)
            except Exception:
                EventoBD.deletarInscrito(idEvento, idUsuario)
                raise
        except Exception:
            if caminhoComprovante:
                Path(caminhoComprovante).unlink(missing_ok=True)
            raise
        tasks.add_task(
            enviarEmailConfirmacaoEvento,
            str(usuario.email),
            evento.id,
            usuario.id,
            dadosInscrito.tipoVaga,
        )
        return inscrito

    # Métodos adicionados do InscritosControlador
    @staticmethod
    def getInscritos(idEvento: str) -> list[InscritoLer]:
        """
        Recupera os inscritos de um evento.

        :param idEvento: Identificador único do evento.

        :return: Lista de inscritos do evento.
        """
        inscritos = EventoBD.listarInscritosEvento(idEvento)
        resultado = []

        for inscrito in inscritos:
            usuario = UsuarioBD.buscar("_id", inscrito.idUsuario)
            resultado.append(
                InscritoLer(
                    **inscrito.model_dump(exclude={"comprovante"}),
                    comprovante="disponivel" if inscrito.comprovante else None,
                    nome=usuario.nome,
                    cpf=usuario.cpf,
                    email=str(usuario.email),
                    curso=usuario.curso,
                    tipoConta=usuario.tipoConta.value,
                )
            )

        return resultado

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
    def verificarInscricao(
        idEvento: str, idUsuario: str, statusComprovante: str, tasks: BackgroundTasks
    ) -> Inscrito:
        """Registra a aceitação ou rejeição do comprovante de uma inscrição."""
        evento = EventoControlador.getEvento(idEvento)
        inscrito = EventoBD.buscarInscrito(idEvento, idUsuario)
        if not inscrito.comprovante:
            raise NaoEncontradoExcecao(message="A inscrição não possui comprovante.")
        EventoBD.atualizarInscrito(
            idEvento, idUsuario, {"statusComprovante": statusComprovante}
        )
        if statusComprovante == "rejeitado":
            usuario = UsuarioBD.buscar("_id", idUsuario)
            tasks.add_task(
                enviarEmailGenerico,
                str(usuario.email),
                f"PET-Info - Comprovante do evento {evento.titulo}",
                "Seu comprovante foi rejeitado. Acesse sua inscrição para enviar um novo arquivo.",
            )
        return EventoBD.buscarInscrito(idEvento, idUsuario)

    @staticmethod
    def editarInscrito(
        idEvento: str, idUsuario: str, inscritoAtualizar: InscritoAtualizar
    ):
        """
        Edita o tipo de vaga de um inscrito em um evento.

        :param idEvento: Identificador único do evento.
        :param idUsuário: Identificador único do usuário a ser editado.
        :param inscritoAtualizar: Tipo de vaga atual do inscrito a ser editado.

        :raises SemVagasDisponiveisExcecao: Se não houver vaga disponível no novo tipo.
        """
        # Recupera o inscrito
        inscrito = EventoBD.buscarInscrito(idEvento, idUsuario)
        # Atualiza o tipo de vaga se necessário
        if (
            inscritoAtualizar.tipoVaga
            and inscritoAtualizar.tipoVaga != inscrito.tipoVaga
        ):
            EventoBD.trocarTipoVaga(idEvento, idUsuario, inscrito.tipoVaga, inscritoAtualizar.tipoVaga)

        if inscritoAtualizar.nivelConhecimento is not None:
            EventoBD.atualizarInscrito(
                idEvento,
                idUsuario,
                {"nivelConhecimento": inscritoAtualizar.nivelConhecimento},
            )
        return EventoBD.buscarInscrito(idEvento, idUsuario)

    @staticmethod
    def substituirComprovante(
        idEvento: str, idUsuario: str, comprovante: UploadFile
    ) -> Inscrito:
        evento = EventoControlador.getEvento(idEvento)
        inscrito = EventoBD.buscarInscrito(idEvento, idUsuario)
        if evento.valor == 0:
            raise ComprovanteInvalido(
                message="Eventos gratuitos não possuem comprovante."
            )
        if not validaComprovante(comprovante.file):
            raise ComprovanteInvalido(message="Comprovante inválido.")
        comprovante.file.seek(0)
        novo = armazenaComprovante(idEvento, idUsuario, comprovante.file)
        if not novo:
            raise ImagemNaoSalvaExcecao()
        try:
            EventoBD.atualizarInscrito(
                idEvento,
                idUsuario,
                {"comprovante": str(novo), "statusComprovante": "pendente"},
            )
        except Exception:
            Path(novo).unlink(missing_ok=True)
            raise
        if inscrito.comprovante and Path(inscrito.comprovante) != Path(novo):
            Path(inscrito.comprovante).unlink(missing_ok=True)
        return EventoBD.buscarInscrito(idEvento, idUsuario)

    @staticmethod
    def enviarComunicado(
        idEvento: str,
        assunto: str,
        mensagem: str,
        idInscrito: str | None,
        anexos: list[tuple[str, bytes]],
        confirmarSemAnexo: bool,
        tasks: BackgroundTasks,
    ):
        EventoControlador.getEvento(idEvento)
        if not assunto or not mensagem:
            raise ErroNaAlteracaoExcecao(message="Assunto e mensagem são obrigatórios.")
        if "em anexo" in mensagem.lower() and not anexos and not confirmarSemAnexo:
            raise ErroNaAlteracaoExcecao(
                message="Confirme o envio da mensagem sem anexos."
            )
        inscritos = (
            [EventoBD.buscarInscrito(idEvento, idInscrito)]
            if idInscrito
            else EventoBD.listarInscritosEvento(idEvento)
        )
        for inscrito in inscritos:
            usuario = UsuarioBD.buscar("_id", inscrito.idUsuario)
            tasks.add_task(
                enviarEmailComAnexos, str(usuario.email), assunto, mensagem, anexos
            )
        return {"destinatarios": len(inscritos)}

    @staticmethod
    def removerInscrito(idEvento: str, idUsuario: str):
        """
        Remove um inscrito de um evento.

        :param idEvento: Identificador único do evento.
        :param idUsuario: Dados do usuário a ser removido.

        :raises NaoEncontradoExcecao: Se o inscrito não for encontrado no evento.
        """
        # Recupera o evento (valida a existência)
        evento = EventoControlador.getEvento(idEvento)
        inscrito = EventoBD.buscarInscrito(idEvento, idUsuario)
        EventoBD.deletarInscrito(idEvento, idUsuario)
        usuario = UsuarioBD.buscar("_id", idUsuario)
        UsuarioBD.removerEventoInscrito(idUsuario, idEvento)
        if inscrito.comprovante:
            Path(inscrito.comprovante).unlink(missing_ok=True)
        return usuario, evento
