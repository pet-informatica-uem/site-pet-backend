from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from datetime import datetime
from app.model.validator.dadosEvento import ValidarEvento
from app.model.inscritosEventoBD import InscritosEventoBD


class EventoBD:
    def __init__(self) -> None:
        cliente = MongoClient()
        db = cliente["petBD"]
        self.__colecao = db["eventos"]
        self.__validarEvento = ValidarEvento().evento()

    def cadastrarEvento(self, dadosEvento: object) -> dict:
        dadosEvento["data criação"] = datetime.now()
        dadosEvento["vagas ofertadas"]["vagas preenchidas com notebook"] = 0
        dadosEvento["vagas ofertadas"]["vagas preenchidas sem notebook"] = 0

        if self.__validarEvento.validate(dadosEvento):
            try:
                resultado = self.__colecao.insert_one(dadosEvento)
                InscritosEventoBD().criarListaInscritos(resultado.inserted_id)

                return {"mensagem": "Evento cadastrado com sucesso!", "status": "200"}
            except DuplicateKeyError:
                return {"mensagem": "Evento já cadastrado!", "status": "409"}
        else:
            return {"mensagem": self.__validarEvento.errors, "status": "400"}

    def removerEvento(self, nomeEvento: str) -> dict:
        resultado = self.__colecao.find_one({"nome evento": nomeEvento})
        if resultado:
            InscritosEventoBD().deletarListaInscritos(resultado["_id"])
            self.__colecao.delete_one({"nome evento": nomeEvento})
            return {"mensagem": "Evento removido com sucesso!", "status": "200"}
        else:
            return {"mensagem": "Evento não encontrado!", "status": "404"}

    def atualizarEvento(self, nomeEvento: str, dadosEvento: object) -> dict:
        if self.getEvento(nomeEvento)["status"] == "404":
            return {"mensagem": "Evento não encontrado!", "status": "404"}

        if self.__validarEvento.validate(dadosEvento):
            try:
                self.__colecao.update_one(
                    {"nome evento": nomeEvento}, {"$set": dadosEvento}
                )
                return {"mensagem": "Evento atualizado com sucesso!", "status": "200"}
            except DuplicateKeyError:
                return {"mensagem": "Evento já cadastrado!", "status": "409"}
        else:
            return {"mensagem": self.__validarEvento.errors, "status": "400"}

    def listarEventos(self) -> list:
        return {"mensagem": list(self.__colecao.find({}, {"_id": 0})), "status": "200"}

    def getEvento(self, nomeEvento: str) -> dict:
        resultado = self.__colecao.find_one({"nome evento": nomeEvento})
        if resultado:
            return {"mensagem": resultado, "status": "200"}
        else:
            return {"mensagem": "Evento não encontrado!", "status": "404"}

    def getEventoId(self, nomeEvento: str) -> dict:
        resultado = self.__colecao.find_one({"nome evento": nomeEvento})
        if resultado:
            return {"mensagem": resultado["_id"], "status": "200"}
        else:
            return {"mensagem": "Evento não encontrado!", "status": "404"}

    def setVagas(self, nomeEvento: str, tipoVaga: str) -> dict:
        vagasOfertadas = self.getVagas(nomeEvento)
        if vagasOfertadas["status"] == "404":
            return {"mensagem": "Evento não encontrado!", "status": "404"}

        vagasOfertadas = vagasOfertadas["mensagem"]

        if tipoVaga == "com notebook" or tipoVaga == "sem notebook":
            if (
                vagasOfertadas["vagas preenchidas " + tipoVaga]
                < vagasOfertadas["vagas " + tipoVaga]
            ):
                resultado = self.__colecao.update_one(
                    {"nome evento": nomeEvento},
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
                return {"mensagem": "Não há vagas disponíveis.", "status": "404"}

        else:
            return {"mensagem": "Tipo de vaga inválido.", "status": "404"}

    def getVagas(self, nomeEvento: str) -> dict:
        resultado = self.__colecao.find_one({"nome evento": nomeEvento})
        if resultado:
            return {"mensagem": resultado["vagas ofertadas"], "status": "200"}
        else:
            return {"mensagem": "Evento não encontrado!", "status": "404"}
