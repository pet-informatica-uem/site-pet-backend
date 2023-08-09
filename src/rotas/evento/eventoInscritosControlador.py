import logging
from typing import BinaryIO



from src.modelos.excecao import EmailNaoFoiEnviadoExcecao, NivelDeConhecimentoErradoExcecao, UsuarioNaoEncontradoExcecao, NaoEncontradoExcecao, TipoDeInscricaoErradoExcecao, ErroInternoExcecao
from src.config import config
from src.email.operacoesEmail import emailConfirmacaoEvento
from src.modelos.evento.inscritosEventoBD import InscritosEventoBD
from src.modelos.usuario.usuarioBD import UsuarioBD
from src.modelos.evento.evento import DadosEvento
from src.modelos.evento.eventoBD import EventoBD

class InscritosEventoControlador:
    def __init__(self):
        self.__inscritosEvento = InscritosEventoBD()

    def getInscritosEvento(self, idEvento: str) -> dict:
        inscritosEvento: list = self.__inscritosEvento.getListaInscritos(idEvento)  # type: ignore

        if inscritosEvento["status"] == "404":  # type: ignore
            return inscritosEvento  # type: ignore

        # lista de usuários inscritos no event
        idsUsuarios: list = [
            usuario["idUsuario"] for usuario in inscritosEvento["mensagem"]  # type: ignore
        ]
        usuarios: dict = UsuarioBD().getListaUsuarios(idsUsuarios)  # type: ignore

        if usuarios["status"] == "404":
            return usuarios

        usuarios: map = list(map(self.__limparUsuarios, usuarios["mensagem"]))  # type: ignore
        usuarios = list(usuarios)  # type: ignore

        # concatena os dicionarios dos inscritos no evento com o dicionario do usuário, o qual contem nome, email e curso
        for inscrito, usuario in zip(inscritosEvento["mensagem"], usuarios):  # type: ignore
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


    def inscricaoEventoControlador(   
        self, idUsuario: str,
        idEvento: str,
        nivelConhecimento: str | None,
        tipoDeInscricao: str,
        pagamento: bool | None,
    ) -> dict:
        if tipoDeInscricao not in ["sem notebook", "com notebook"]:
            raise TipoDeInscricaoErradoExcecao()

        usuarioBD = UsuarioBD()
        dicionarioUsuario : dict = usuarioBD.getUsuario(idUsuario)
        if not dicionarioUsuario:
            raise UsuarioNaoEncontradoExcecao()

        eventoBD = EventoBD()
        dicionarioEvento : dict = eventoBD.getEvento(idEvento)
        dicionarioEnvioGmail : dict = {
            "nome evento": dicionarioEvento["nome evento"],
            "local": dicionarioEvento["local"],
            "data/hora evento": dicionarioEvento["data/hora evento"],
            "pré-requisitos": dicionarioEvento["pré-requisitos"],
        }
        if not dicionarioEvento:
            raise NaoEncontradoExcecao()

        if nivelConhecimento not in ["1", "2", "3", "4", "5", None]:
            raise NivelDeConhecimentoErradoExcecao() 

        inscritos = InscritosEventoBD()
        inscrito: dict = {
            "idEvento": idEvento,
            "idUsuario": idUsuario,
            "nivelConhecimento": nivelConhecimento,
            "tipoInscricao": tipoDeInscricao,
            "pagamento": pagamento,
        }

        situacaoInscricao: bool = inscritos.setInscricao(inscrito)
        if not situacaoInscricao:
            raise ErroInternoExcecao(message = "Nao foi possivel realizar a inscricao")

        emailConfirmacaoEvento(
            emailPet=config.EMAIL_SMTP,
            senhaPet=config.SENHA_SMTP,
            emailDestino=dicionarioUsuario['email'],
            evento=dicionarioEnvioGmail
        )

        return situacaoInscricao
