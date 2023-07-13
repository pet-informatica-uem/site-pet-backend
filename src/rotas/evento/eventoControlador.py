import logging
from src.email.operacoesEmail import emailConfirmacaoEvento
from typing import BinaryIO

from src.img.operacoesImagem import (
    armazenaArteEvento,
    armazenaQrCodeEvento,
    deletaImagem,
    validaImagem,
)
from src.config import config
from src.modelos.evento.evento import DadosEvento
from src.modelos.evento.eventoBD import EventoBD
from src.modelos.evento.inscritosEventoBD import InscritosEventoBD
from src.modelos.usuario.usuarioBD import UsuarioBD


def controladorNovoEvento(
    dadosEvento: DadosEvento, imagens: dict[str, BinaryIO | None]
) -> dict:
    # Valida as imagens
    if not validaImagem(imagens["arteEvento"]):  # type: ignore
        return {"mensagem": "Arte do evento inválida.", "status": "400"}

    if imagens["arteQrcode"] and not validaImagem(imagens["arteQrcode"]):
        return {"mensagem": "Imagem do qrCode inválida.", "status": "400"}

    # Armazena as imagens
    caminhoArte = armazenaArteEvento(dadosEvento.nomeEvento, imagens["arteEvento"])  # type: ignore
    dadosEvento.caminhoArteEvento = caminhoArte  # type: ignore

    if imagens["arteQrcode"]:
        caminhoQrCode = armazenaQrCodeEvento(
            dadosEvento.nomeEvento, imagens["arteQrcode"]
        )
        dadosEvento.caminhoArteQrcode = caminhoQrCode  # type: ignore

    # Valida os dados e registra o evento no bd
    try:
        conexao = EventoBD()
        retorno = conexao.cadastrarEvento(dadosEvento.paraBD())
        if retorno["status"] != "200":
            deletaImagem(dadosEvento.nomeEvento)
            return retorno
        idEvento = conexao.getEventoID(dadosEvento.nomeEvento)
        logging.info(f"Evento cadastrado com id: {idEvento}")

        return {"mensagem": "Evento cadastrado com sucesso!", "status": "201"}

    except Exception as e:
        logging.warning("Problema para adicionar eventos.")
        return {"mensagem": "Problema interno.", "status": "400"}


def controladorEditarEvento(idEvento, dadosEvento: DadosEvento, imagens: dict):
    try:
        conexao = EventoBD()

        # Verfica se o evento existe e recupera os dados dele
        eventoOld = conexao.getEvento(idEvento)
        if eventoOld["status"] == "404":
            return {"mensagem": "Evento não encontrado!", "status": "404"}
        dadosEventoOld = eventoOld["mensagem"]

        # Valida as imagens (se existirem)
        if imagens["arteEvento"] and not validaImagem(imagens["arteEvento"]):
            return {"mensagem": "Arte do evento inválida.", "status": "400"}

        if imagens["arteQrcode"] and not validaImagem(imagens["arteQrcode"]):
            return {"mensagem": "Imagem do qrCode inválida.", "status": "400"}

        dadosEvento.caminhoArteEvento = dadosEventoOld["arte evento"]
        dadosEvento.caminhoArteQrcode = dadosEventoOld["arte qrcode"]

        # Verifica os dados e atualiza o evento
        retorno = conexao.atualizarEvento(idEvento, dadosEvento.paraBD())

        if retorno["status"] != "200":
            return {"mensagem": retorno["mensagem"], "status": retorno["status"]}

        # Deleta as imagens antigas e armazena as novas
        if imagens["arteEvento"]:
            deletaImagem(dadosEventoOld["nome evento"], ["eventos", "arte"])
            dadosEvento.caminhoArteEvento = armazenaArteEvento(
                dadosEvento.nomeEvento, imagens["arteEvento"]
            )  # type: ignore
        else:
            dadosEvento.caminhoArteEvento = dadosEventoOld["arte evento"]

        if imagens["arteQrcode"]:
            deletaImagem(dadosEventoOld["nome evento"], ["eventos", "qrcode"])
            dadosEvento.caminhoArteQrcode = armazenaQrCodeEvento(
                dadosEvento.nomeEvento, imagens["arteQrcode"]
            )  # type: ignore
        else:
            dadosEvento.caminhoArteQrcode = dadosEventoOld["arte qrcode"]

        # Caso alguma imagem tenha sido alterada, atualiza o evento novamente para adicionar o caminho para as imagens
        if imagens["arteEvento"] or imagens["arteQrcode"]:
            conexao.atualizarEvento(idEvento, dadosEvento.paraBD())

        return {"mensagem": "Evento atualizado com sucesso!", "status": "200"}

    except Exception as e:
        logging.warning("Problema para editar eventos.")
        return {"mensagem": str(e), "status": "500"}


def controladorDeletaEvento(idEvento: str):
    # Verifica se o evento existe

    conexao: EventoBD = EventoBD()
    evento: dict = conexao.getEvento(idEvento)

    if evento["status"] == "400":
        return {"status": "400", "mensagem": "Evento não encontrado."}

    if conexao.removerEvento(idEvento)["status"] != "200":
        return {"status": "500", "mensagem": "Problema para remover o evento"}

    deletaImagem(evento["mensagem"]["nome evento"])
    return {"status": "200", "mensagem": "Evento removido com sucesso."}


class EventoController:
    def __init__(self):
        self.__evento = EventoBD()

    def listarEventos(self) -> dict:
        eventos: dict = self.__evento.listarEventos()

        if eventos["status"] == "404":
            return eventos

        for evento in eventos["mensagem"]:
            evento["_id"] = str(evento["_id"])

        return eventos


def inscricaoEventoControlador(
    idUsuario: str,
    idEvento: str,
    nivelConhecimento: str | None,
    tipoDeInscricao: str,
    pagamento: bool | None,
) -> dict:
    if tipoDeInscricao not in ["sem notebook", "com notebook"]:
        return {
            "mensagem": "Formato do tipo de inscricao em formato errado, deveria ser: com notebook ou sem notebook",
            "status": "400",
        }

    usuarioBD = UsuarioBD()
    situacaoUsuario: dict = usuarioBD.getUsuario(idUsuario)
    if situacaoUsuario["status"] != "200":
        return {
            "mensagem": "Usuario nao encontrado",
            "status": "404",
        }

    eventoBD = EventoBD()
    situacaoEvento: dict = eventoBD.getEvento(idEvento)
    if situacaoEvento["status"] != "200":
        return situacaoEvento

    if nivelConhecimento not in ["1", "2", "3", "4", "5", None]:
        return {"mensagem": "Nivel de conhecimento invalido", "status": "400"}

    inscritos = InscritosEventoBD()
    inscrito: dict = {
        "idEvento": idEvento,
        "idUsuario": idUsuario,
        "nivelConhecimento": nivelConhecimento,
        "tipoInscricao": tipoDeInscricao,
        "pagamento": pagamento,
    }

    situacaoInscricao: dict = inscritos.setInscricao(inscrito)
    if situacaoInscricao["status"] == "200":
        dicionarioEnvioGmail: dict = {
            "nome evento": situacaoEvento["mensagem"]["nome evento"],
            "local": situacaoEvento["mensagem"]["local"],
            "data/hora evento": situacaoEvento["mensagem"]["data/hora evento"],
            "pré-requisitos": situacaoEvento["mensagem"]["pré-requisitos"],
        }

        respostaEmail: dict = emailConfirmacaoEvento(
            emailPet=config.EMAIL_SMTP,
            senhaPet=config.SENHA_SMTP,
            emailDestino=situacaoUsuario["mensagem"]["email"],
            evento=dicionarioEnvioGmail,
        )

        if respostaEmail["status"] != "200":
            return respostaEmail

    return situacaoInscricao
