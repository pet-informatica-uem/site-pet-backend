import logging
from datetime import datetime

from fastapi import BackgroundTasks, UploadFile

from src.email.operacoesEmail import enviarEmailConfirmacaoEvento
from src.img.operacoesImagem import armazenaComprovante, deletaImagem, validaComprovante
from src.modelos.bd import EventoBD, InscritoBD, UsuarioBD, cliente
from src.modelos.evento.evento import Evento
from src.modelos.excecao import (
    APIExcecaoBase,
    ComprovanteInvalido,
    ComprovanteObrigatorioExcecao,
    ForaDoPeriodoDeInscricaoExcecao,
    SemVagasDisponiveisExcecao,
)
from src.modelos.inscrito.inscrito import Inscrito
from src.modelos.inscrito.inscritoClad import (
    InscritoAtualizar,
    InscritoCriar,
    InscritoDeletar,
    TipoVaga,
)
from src.modelos.usuario.usuario import Usuario
from src.rotas.evento.eventoControlador import EventoControlador


class InscritosControlador:
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
            raise ForaDoPeriodoDeInscricaoExcecao()

        # Verifica se há vagas disponíveis
        if dadosInscrito.tipoVaga == TipoVaga.COM_NOTE:
            if evento.vagasDisponiveisComNote == 0:
                raise SemVagasDisponiveisExcecao()
        else:
            if evento.vagasDisponiveisSemNote == 0:
                raise SemVagasDisponiveisExcecao()

        if evento.valor != 0:
            if comprovante:
                if not validaComprovante(comprovante.file):
                    raise ComprovanteInvalido()

                deletaImagem(idUsuario, ["eventos", evento.id, "comprovantes"])
                caminhoComprovante = armazenaComprovante(
                    evento.id, idUsuario, comprovante.file
                )
            else:
                raise ComprovanteObrigatorioExcecao()
        else:
            caminhoComprovante = None

        d = {
            "idEvento": idEvento,
            "idUsuario": idUsuario,
            "dataInscricao": datetime.now(),
        }

        d.update(**dadosInscrito.model_dump())
        inscrito = Inscrito(**d)
        inscrito.comprovante = str(caminhoComprovante) if caminhoComprovante else None  # type: ignore

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

            InscritoBD.criar(inscrito)
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
        tasks.add_task(
            enviarEmailConfirmacaoEvento,
            usuario.email,
            evento.id,
            inscrito.tipoVaga,
        )

    @staticmethod
    def getInscritos(idEvento: str):
        return InscritoBD.listarInscritosEvento(idEvento)

    @staticmethod
    def getInscrito(idEvento: str, idInscrito: str):
        return InscritoBD.buscar(idEvento, idInscrito)

    @staticmethod
    def editarInscrito(idEvento: str, idInscrito: str, inscrito: InscritoAtualizar):
        # Recupera o inscrito
        inscritoOld: Inscrito = InscritoBD.buscar(idEvento, idInscrito)

        # Verifica se o tipo de vaga foi alterado e se há vagas disponíveis
        if inscrito.tipoVaga != None and inscrito.tipoVaga != inscritoOld.tipoVaga:
            # Recupera o evento
            evento: Evento = EventoControlador.getEvento(idEvento)

            if inscrito.tipoVaga == TipoVaga.COM_NOTE:
                if evento.vagasDisponiveisComNote == 0:
                    raise SemVagasDisponiveisExcecao()
                evento.vagasDisponiveisSemNote += 1
                evento.vagasDisponiveisComNote -= 1
            elif inscrito.tipoVaga == TipoVaga.SEM_NOTE:
                if evento.vagasDisponiveisSemNote == 0:
                    raise SemVagasDisponiveisExcecao()
                evento.vagasDisponiveisComNote += 1
                evento.vagasDisponiveisSemNote -= 1

            # Atualiza o evento no bd
            EventoBD.atualizar(evento)

        d = inscritoOld.model_dump(by_alias=True)
        d.update(**inscrito.model_dump(exclude_none=True))
        d = Inscrito(**d)  # type: ignore

        # Atualiza o inscrito no bd
        InscritoBD.atualizar(d)

    @staticmethod
    def removerInscrito(inscrito: InscritoDeletar):
        # Recupera o evento
        evento: Evento = EventoControlador.getEvento(inscrito.idEvento)

        # Verifica se está no período de inscrição
        if (
            evento.inicioInscricao > datetime.now()
            or evento.fimInscricao < datetime.now()
        ):
            raise ForaDoPeriodoDeInscricaoExcecao()

        # Recupera o inscrito
        inscritoRecuperado: Inscrito = InscritoBD.buscar(
            inscrito.idEvento, inscrito.idUsuario
        )

        if inscritoRecuperado.tipoVaga == TipoVaga.COM_NOTE:
            evento.vagasDisponiveisComNote += 1
        elif inscritoRecuperado.tipoVaga == TipoVaga.SEM_NOTE:
            evento.vagasDisponiveisSemNote += 1

        # Recupera o usuário
        usuario: Usuario = UsuarioBD.buscar("_id", inscrito.idUsuario)

        # Remove o evento na lista de eventos inscritos do usuário
        usuario.eventosInscrito.remove(inscrito.idEvento)

        # Realiza as operações no BD usando uma transação
        session = cliente.start_session()
        try:
            session.start_transaction()

            EventoBD.atualizar(evento)
            InscritoBD.deletar(inscrito.idEvento, inscrito.idUsuario)
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
