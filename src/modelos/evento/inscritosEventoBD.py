from datetime import datetime
from bson.objectid import ObjectId
from pymongo import MongoClient

from modelos.evento.inscritosEvento import ValidarInscritosEvento


class InscritosEventoBD:
    def __init__(self) -> None:
        cliente = MongoClient()
        db = cliente["petBD"]
        self.__colecao = db["inscritos eventos"]
        self.__validarEvento = ValidarInscritosEvento()

    def criarListaInscritos(self, dadosListaInscritos: dict) -> dict:
        if self.__validarEvento.vagasEvento().validate(dadosListaInscritos):
            return {
                "mensagem": self.__validarEvento.vagasEvento().errors,
                "status": "400",
            }

        if (
            self.__colecao.find_one({"idEvento": dadosListaInscritos["idEvento"]})
            != None
        ):
            return {"mensagem": "Evento já cadastrado!", "status": "409"}

        self.__colecao.insert_one(dadosListaInscritos)
        return {"mensagem": "Lista de inscritos criada com sucesso!", "status": "200"}

    def deletarListaInscritos(self, idEvento: str) -> dict:
        resultado = self.__colecao.delete_one({"idEvento": idEvento})
        if resultado.deleted_count == 1:
            return {
                "mensagem": "Lista de inscritos deletada com sucesso!",
                "status": "200",
            }
        else:
            return {"mensagem": "Evento não encontrado!", "status": "404"}

    def atualizarVagasOfertadas(self, idEvento: str, dadosVagas: dict) -> dict:
        idEvento = ObjectId(idEvento)

        try:
            self.__colecao.update_one(
                {"idEvento": idEvento},
                {
                    "$set": {
                        "vagas ofertadas": {
                            "vagas com notebook": dadosVagas["vagas ofertadas"][
                                "vagas com notebook"
                            ],
                            "vagas sem notebook": dadosVagas["vagas ofertadas"][
                                "vagas sem notebook"
                            ],
                        }
                    }
                },
            )
            return {
                "mensagem": "Quantidade de vagas atualizadas com sucesso!",
                "status": "200",
            }
        except:
            return {
                "mensagem": "Não foi possível atualizar a quantidade de vagas.",
                "status": "404",
            }

    def getListaInscritos(self, idEvento: str) -> dict:
        idEvento = ObjectId(idEvento)
        resultado = self.__colecao.find_one({"idEvento": idEvento})

        if resultado:
            return {"mensagem": resultado["inscritos"], "status": "200"}
        else:
            return {"mensagem": "Evento não encontrado!", "status": "404"}

    def setInscricao(self, dadosInscricao: dict) -> dict:
        if self.__validarEvento.inscricao().validate(dadosInscricao):
            return {
                "mensagem": self.__validarEvento.inscritos().errors, # type: ignore
                "status": "400",
            }

        idEvento = ObjectId(dadosInscricao["idEvento"])

        usuariosInscritos = self.__colecao.find_one(
            {"idEvento": idEvento, "inscritos.idUsuario": dadosInscricao["idUsuario"]}
        )

        if usuariosInscritos:
            return {"mensagem": "Usuário já inscrito!", "status": "409"}

        vagasOfertadas = self.__setVaga(idEvento, dadosInscricao["tipoInscricao"])
        if vagasOfertadas["status"] != "200":
            return {
                "mensagem": vagasOfertadas["mensagem"],
                "status": vagasOfertadas["status"],
            }

        self.__colecao.update_one(
            {"idEvento": idEvento},
            {
                "$push": {
                    "inscritos": {
                        "idUsuario": dadosInscricao["idUsuario"],
                        "data/hora": datetime.now(),
                        "pagamento": dadosInscricao["pagamento"],
                        "presente": False,
                        "nível conhecimento": dadosInscricao["nivelConhecimento"],
                        "tipo inscrição": dadosInscricao["tipoInscricao"],
                    }
                }
            },
        )

        return {"mensagem": "Usuário inscrito com sucesso!", "status": "200"}

    def setPresenca(self, idEvento: str, idUsuario: str) -> dict:
        idEvento = ObjectId(idEvento)

        if self.__colecao.find_one(
            {"idEvento": idEvento, "inscritos.idUsuario": idUsuario}
        ):
            if self.__colecao.find_one(
                {
                    "idEvento": idEvento,
                    "inscritos": {
                        "$elemMatch": {"idUsuario": idUsuario, "pagamento": True}
                    },
                }
            ):
                self.__colecao.update_one(
                    {"idEvento": idEvento, "inscritos.idUsuario": idUsuario},
                    {"$set": {"inscritos.$.presente": True}},
                )
                return {"mensagem": "Presença cadastrada!", "status": "200"}
            else:
                return {"mensagem": "Usuário não pagou o evento!", "status": "409"}
        else:
            return {"mensagem": "Usuário não inscrito no evento!", "status": "404"}

    def setPagamento(self, idEvento: str, idUsuario: str) -> dict:
        idEvento = ObjectId(idEvento)
        resultado = self.__colecao.update_one(
            {"idEvento": idEvento, "inscritos.idUsuario": idUsuario},
            {"$set": {"inscritos.$.pagamento": True}},
        )

        if resultado.modified_count == 1:
            return {"mensagem": "Pagamento registrado com sucesso!", "status": "200"}
        else:
            return {"mensagem": "Usuário não encontrado!", "status": "404"}

    def __setVaga(self, idEvento: str, tipoVaga: str) -> dict:
        idEvento = ObjectId(idEvento)
        vagasOfertadas = self.getVagas(idEvento)
        if vagasOfertadas["status"] == "404":
            return {"mensagem": vagasOfertadas["mensagem"], "status": "404"}

        vagasOfertadas = vagasOfertadas["mensagem"]

        if tipoVaga == "com notebook" or tipoVaga == "sem notebook":
            if (
                vagasOfertadas["vagas preenchidas " + tipoVaga]
                < vagasOfertadas["vagas " + tipoVaga]
            ):
                resultado = self.__colecao.update_one(
                    {"idEvento": idEvento},
                    {"$inc": {"vagas ofertadas.vagas preenchidas " + tipoVaga: 1}},
                )
                if resultado.modified_count > 0:
                    return {"mensagem": "Vaga adicionada com sucesso!", "status": "200"}
                else:
                    return {
                        "mensagem": "Não foi possível adicionar a vaga.",
                        "status": "404",
                    }
            else:
                return {"mensagem": "Não há vagas disponíveis.", "status": "410"}

        else:
            return {"mensagem": "Tipo de vaga inválido.", "status": "404"}

    def getVagas(self, idEvento: str) -> dict:
        idEvento = ObjectId(idEvento)
        resultado = self.__colecao.find_one({"idEvento": idEvento})

        if resultado:
            return {"mensagem": resultado["vagas ofertadas"], "status": "200"}
        else:
            return {"mensagem": "Evento não encontrado!", "status": "404"}
