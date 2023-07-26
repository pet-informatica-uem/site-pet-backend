from datetime import datetime

from bson.objectid import ObjectId
from pymongo import MongoClient

from src.modelos.evento.inscritosEvento import ValidarInscritosEvento
from src.modelos.excecao import JaExisteExcecao, NaoEncontradoExcecao, NaoAtualizadaExcecao, ErroNaAlteracaoExcecao, SemVagasDisponiveisExcecao, TipoVagaInvalidoExcecao



class InscritosEventoBD:
    def __init__(self) -> None:
        cliente = MongoClient()
        db = cliente["petBD"]
        self.__colecao = db["inscritos eventos"]
        self.__validarEvento = ValidarInscritosEvento()

    def criarListaInscritos(self, dadosListaInscritos: dict) -> bool:
        if self.__validarEvento.vagasEvento().validate(dadosListaInscritos):
            raise Exception(self.__validarEvento.vagasEvento().errors)
        
        if (
            self.__colecao.find_one({"idEvento": dadosListaInscritos["idEvento"]})
            != None
        ):
            raise JaExisteExcecao(messege = "Evento já cadastrado! ")

        self.__colecao.insert_one(dadosListaInscritos)
        return True

    def deletarListaInscritos(self, idEvento: str) -> bool:
        resultado = self.__colecao.delete_one({"idEvento": idEvento})
        if resultado.deleted_count == 1:
            return True
        else:
            raise NaoEncontradoExcecao(messege = "Evento não encontrado!")

    def atualizarVagasOfertadas(self, idEvento: str, dadosVagas: dict) -> str:
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
            return str(idEvento)
        except:
            raise NaoAtualizadaExcecao(messege = "Não foi possível atualizar a quantidade de vagas. ")

    def getListaInscritos(self, idEvento: str) -> bool:
        idEvento = ObjectId(idEvento)
        resultado = self.__colecao.find_one({"idEvento": idEvento})

        if resultado:
            return resultado["inscritos"]
        else:
            raise NaoEncontradoExcecao(messege = "Evento não encontrado! ")

    def setInscricao(self, dadosInscricao: dict) -> dict:
        if self.__validarEvento.inscricao().validate(dadosInscricao):
            raise Exception(self.__validarEvento.inscritos().errors)

        idEvento = ObjectId(dadosInscricao["idEvento"])

        usuariosInscritos = self.__colecao.find_one(
            {"idEvento": idEvento, "inscritos.idUsuario": dadosInscricao["idUsuario"]}
        )

        if usuariosInscritos:
            raise JaExisteExcecao(messege = "Usuário já inscrito! ")

        # duvida, quando gera um erro na funcao __setVaga, eu preciso tratar esse erro?
        self.__setVaga(idEvento, dadosInscricao["tipoInscricao"])

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

        return True

    def setPresenca(self, idEvento: str, idUsuario: str) -> bool:
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
                return True
            else:
                raise NaoEncontradoExcecao(messege = "Pagamento não encontrado. ")
        else:
            raise NaoEncontradoExcecao(messege = "Usuário não encontrado na lista de incritos. ")

    def setPagamento(self, idEvento: str, idUsuario: str) -> bool:
        idEvento = ObjectId(idEvento)
        resultado = self.__colecao.update_one(
            {"idEvento": idEvento, "inscritos.idUsuario": idUsuario},
            {"$set": {"inscritos.$.pagamento": True}},
        )

        if resultado.modified_count == 1:
            return True
        else:
            return NaoEncontradoExcecao(messege = "Usuário não encontrado na lista de incritos. ")

    def __setVaga(self, idEvento: str, tipoVaga: str) -> bool:
        idEvento = ObjectId(idEvento)
        vagasOfertadas = self.getVagas(idEvento)

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
                    return True
                else:
                    raise NaoAtualizadaExcecao(messege = "Não foi possível adicionar a vaga.")
            else:
                raise NaoAtualizadaExcecao(messege = "Não há vagas disponíveis.")

        else:
            raise TipoVagaInvalidoExcecao()

    def getVagas(self, idEvento: str) -> dict:
        idEvento = ObjectId(idEvento)
        resultado = self.__colecao.find_one({"idEvento": idEvento})

        if resultado:
            return resultado["vagas ofertadas"]
        else:
            raise NaoEncontradoExcecao(messege = "Evento não encontrado! ")
