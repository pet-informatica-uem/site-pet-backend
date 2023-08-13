import logging
from datetime import datetime  # nao apagar
from typing import BinaryIO

from src.config import config
from src.email.operacoesEmail import emailConfirmacaoEvento
from src.modelos.evento.evento import DadosEvento
from src.modelos.evento.eventoBD import EventoBD
from src.modelos.evento.inscritosEventoBD import InscritosEventoBD
from src.modelos.excecao import (
    EmailNaoFoiEnviadoExcecao,
    ErroInternoExcecao,
    NaoEncontradoExcecao,
    NivelDeConhecimentoErradoExcecao,
    TipoDeInscricaoErradoExcecao,
    UsuarioNaoEncontradoExcecao,
)
from src.modelos.usuario.usuarioBD import UsuarioBD


class InscritosEventoControlador:
    def __init__(self):
        self.__inscritosEvento = InscritosEventoBD()

    def getInscritosEvento(self, idEvento: str) -> list[dict]:
        inscritosEvento: list = self.__inscritosEvento.getListaInscritos(idEvento)  # type: ignore

        # lista de usuários inscritos no event
        idsUsuarios: list = [
            usuario["idUsuario"] for usuario in inscritosEvento  # type: ignore
        ]

        usuarios: dict = UsuarioBD().getListaUsuarios(idsUsuarios)  # type: ignore

        usuarios: map = list(map(self.__limparUsuarios, usuarios["mensagem"]))  # type: ignore
        usuarios = list(usuarios)  # type: ignore

        # concatena os dicionarios dos inscritos no evento com o dicionario do usuário, o qual contem nome, email e curso
        for inscrito, usuario in zip(inscritosEvento, usuarios):  # type: ignore
            inscrito["idUsuario"] = str(inscrito["idUsuario"])
            inscrito.update(usuario)

        return inscritosEvento  # type: ignore

    # tirar o _id, cpf, estado da conta, senha, tipo da conta, data criacao
    def __limparUsuarios(self, dadosUsuario: dict) -> dict:
        dadosUsuario.pop("_id")
        dadosUsuario.pop("cpf")
        dadosUsuario.pop("estado da conta")
        dadosUsuario.pop("senha")
        dadosUsuario.pop("tipo conta")
        dadosUsuario.pop("data criacao")

        return dadosUsuario

    def inscricaoEvento(self, inscrito: dict) -> bool:
        situacaoInscricao: bool = self.__inscritosEvento.setInscricao(inscrito)
        if not situacaoInscricao:
            raise ErroInternoExcecao(message="Nao foi possivel realizar a inscricao")

        return situacaoInscricao
