import time
from datetime import datetime
from PIL import Image

from fastapi import UploadFile

from src.img.operacoesImagem import deletaImagem, validaComprovante, armazenaComprovante
from src.config import config
from src.email.operacoesEmail import emailConfirmacaoEvento
from src.modelos.bd import EventoBD, InscritoBD, UsuarioBD, colecaoInscritos
from src.modelos.evento.evento import Evento
from src.modelos.excecao import APIExcecaoBase
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
        idEvento: str, idUsuario: str, inscrito: InscritoCriar, comprovante: UploadFile
    ):
        # Recupera o evento
        evento: Evento = EventoControlador.getEvento(idEvento)

        # Verifica se está no período de inscrição
        if (
            evento.inicioInscricao > datetime.now()
            or evento.fimInscricao < datetime.now()
        ):
            raise APIExcecaoBase(message="Fora do período de inscrição")

        # Verifica se há vagas disponíveis
        if inscrito.tipoVaga == TipoVaga.COM_NOTE:
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
                caminhoComprovante: str | None = armazenaComprovante(evento.id, idUsuario, comprovante.file)
            else:
                raise APIExcecaoBase(message="Falha ao registrar comprovante")
        else: caminhoComprovante: str| None = None
                                     
        d = {
            "idEvento": idEvento,
            "idUsuario": idUsuario,
            "dataInscricao": datetime.now(),
            "comprovante" : caminhoComprovante, 
        }

        d.update(**inscrito.model_dump())
        d = Inscrito(**d)

        # Cria o inscrito no bd
        InscritoBD.criar(d)

        if inscrito.tipoVaga == TipoVaga.COM_NOTE:
            evento.vagasDisponiveisComNote -= 1
        else:
            evento.vagasDisponiveisSemNote -= 1

        # Atualiza o evento no bd
        EventoBD.atualizar(evento)

        # Recupera o usuário
        usuario: Usuario = UsuarioBD.buscar("_id", idUsuario)

        # Envia email de confirmação de inscrição
        emailConfirmacaoEvento(
            config.EMAIL_SMTP,
            config.SENHA_SMTP,
            usuario.email,
            evento.id,
            inscrito.tipoVaga,
        )

        # Adiciona o evento na lista de eventos inscritos do usuário
        usuario.eventosInscrito.append((idEvento, True))

        # Atualiza o usuário no bd
        UsuarioBD.atualizar(usuario)


    @staticmethod
    def getInscritos(idEvento: str):
        return InscritoBD.listarInscritosEvento(idEvento)

    @staticmethod
    def editarInscrito(idEvento: str, idInscrito: str, inscrito: InscritoAtualizar):
        # Recupera o inscrito
        inscritoOld: Inscrito = InscritoBD.buscar(idEvento, idInscrito)

        # Verifica se o tipo de vaga foi alterado e se há vagas disponíveis
        if inscrito.tipoVaga != None and inscrito.tipoVaga != inscritoOld.tipoVaga:
            # Recupera o evento
            evento: Evento = EventoControlador.getEvento(idEvento)

            if inscrito.tipoVaga:
                if evento.vagasDisponiveisComNote == 0:
                    raise APIExcecaoBase(message="Não há vagas disponíveis com note")
                evento.vagasDisponiveisSemNote += 1
                evento.vagasDisponiveisComNote -= 1
            else:
                if evento.vagasDisponiveisSemNote == 0:
                    raise APIExcecaoBase(message="Não há vagas disponíveis sem note")
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
            raise APIExcecaoBase(message="Fora do período de inscrição")

        # Recupera o inscrito
        inscritoRecuperado: Inscrito = InscritoBD.buscar(
            inscrito.idEvento, inscrito.idUsuario
        )

        if inscritoRecuperado.tipoVaga:
            evento.vagasDisponiveisComNote += 1
        else:
            evento.vagasDisponiveisSemNote += 1

        # Atualiza o evento no bd
        EventoBD.atualizar(evento)

        # Remove o inscrito do bd
        InscritoBD.deletar(inscrito.idEvento, inscrito.idUsuario)

        # Recupera o usuário
        usuario: Usuario = UsuarioBD.buscar("_id", inscrito.idUsuario)

        # Remove o evento na lista de eventos inscritos do usuário
        usuario.eventosInscrito.remove((inscrito.idEvento, True))

        # Atualiza o usuário no bd
        UsuarioBD.atualizar(usuario)
