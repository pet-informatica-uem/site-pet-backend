from app.model.eventoBD import EventoBD
from app.model.usuarioBD import UsuarioBD
from app.model.inscritosEventoBD import InscritosEventoBD
from core.config import config
from app.controllers.operacoesEmail import emailConfirmacaoEvento


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
    if tipoDeInscricao not in ["sem notebook", "com notebook"]
        return {
            "mensagem": "Formato do tipo de inscricao em formato errado, deveria ser: com notebook ou sem notebook",
            "status": "400",
        }

    usuarioBD = UsuarioBD()
    situacaoUsuario = usuarioBD.getUsuario(idUsuario)
    if situacaoUsuario["status"] != "200":
        return {
            "mensagem": "Usuario nao encontrado",
            "status": "404",
        }

    eventoBD = EventoBD()
    situacaoEvento = eventoBD.getEvento(idEvento)
    if situacaoEvento["status"] != "200":
        return situacaoEvento

    if (
       nivelConhecimento not in ["1", "2", "3", "4", "5", None]
    ):
        return {"mensagem": "Nivel de conhecimento invalido", "status": "400"}

    inscritos = InscritosEventoBD()
    inscrito = {
        "idEvento": idEvento,
        "idUsuario": idUsuario,
        "nivelConhecimento": nivelConhecimento,
        "tipoInscricao": tipoDeInscricao,
        "pagamento": pagamento,
    }

    situacaoInscricao = inscritos.setInscricao(inscrito)
    print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
    print(situacaoInscricao)
    if situacaoInscricao["status"] == "200":
        dicionarioEnvioGmail = {
            "nome evento": situacaoEvento["mensagem"]["nome evento"],
            "local": situacaoEvento["mensagem"]["local"],
            "data/hora evento": situacaoEvento["mensagem"]["data/hora evento"],
            "pré-requisitos": situacaoEvento["mensagem"]["pré-requisitos"],
        }

        respostaEmail = emailConfirmacaoEvento(
            emailPet=config.EMAIL_SMTP,
            senhaPet=config.SENHA_SMTP,
            emailDestino=situacaoUsuario["mensagem"]["email"],
            evento=dicionarioEnvioGmail,
        )

        if respostaEmail["status"] != "200":
            return respostaEmail

    return situacaoInscricao
