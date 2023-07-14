from datetime import datetime

from bson.objectid import ObjectId
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

from src.modelos.evento.dadosEvento import ValidarEvento
from src.modelos.evento.inscritosEventoBD import InscritosEventoBD


class EventoBD:
    def __init__(self) -> None:
        cliente = MongoClient()
        db = cliente["petBD"]
        self.__colecao = db["eventos"]
        self.__validarEvento = ValidarEvento().evento()
        self.__insctirosEvento = InscritosEventoBD()

    def cadastrarEvento(self, dadosEvento: dict) -> dict:
        dadosEvento["data criação"] = datetime.now()
        dadosEvento["vagas ofertadas"]["vagas preenchidas com notebook"] = 0
        dadosEvento["vagas ofertadas"]["vagas preenchidas sem notebook"] = 0

        dadosListaInscritos = {
            "idEvento": "",
            "vagas ofertadas": dadosEvento.pop("vagas ofertadas"),
            "inscritos": [],
        }

        # dadosInscricao : VagasEvento = {
        #     "idEvento": "",
        #     "vagas com notebook": 0,
        #     "vagas sem notebook": 0,
        #     "vagas preenchidas com notebook": 0,
        #     "vagas preenchidas sem notebook": 0,
        # }

        if self.__validarEvento.validate(dadosEvento):  # type: ignore
            try:
                # criar documento com os dados do evento
                resultado = self.__colecao.insert_one(dadosEvento)
                dadosListaInscritos["idEvento"] = resultado.inserted_id
                # criar documento com os inscritos do evento
                self.__insctirosEvento.criarListaInscritos(dadosListaInscritos)

                return {"mensagem": "Evento cadastrado com sucesso!", "status": "200"}
            except DuplicateKeyError:
                return {"mensagem": "Evento já cadastrado!", "status": "409"}
        else:
            return {"mensagem": self.__validarEvento.errors, "status": "400"}  # type: ignore

    def removerEvento(self, idEvento: str) -> dict:
        idEvento = ObjectId(idEvento)
        resultado = self.__colecao.find_one({"_id": idEvento})
        if resultado:
            self.__insctirosEvento.deletarListaInscritos(resultado["_id"])
            self.__colecao.delete_one({"_id": idEvento})
            return {"mensagem": "Evento removido com sucesso!", "status": "200"}
        else:
            return {"mensagem": "Evento não encontrado!", "status": "404"}

    def atualizarEvento(self, idEvento: str, dadosEvento: object) -> dict:
        idEvento = ObjectId(idEvento)
        if self.getEvento(idEvento)["status"] == "404":
            return {"mensagem": "Evento não encontrado!", "status": "404"}

        dadosVagasOfertadas = {
            "vagas ofertadas": dadosEvento.pop("vagas ofertadas"),  # type: ignore
        }

        evento = self.__colecao.find_one({"_id": idEvento})
        dadosEvento["data criação"] = evento["data criação"]  # type: ignore

        if self.__validarEvento.validate(dadosEvento):  # type: ignore
            try:
                resultado = self.__colecao.update_one(
                    {"_id": idEvento}, {"$set": dadosEvento}
                )

                resultado = self.__insctirosEvento.atualizarVagasOfertadas(
                    evento["_id"], dadosVagasOfertadas
                )
                if resultado["status"] == "404":
                    return {
                        "mensagem": "Não foi possível atualizar a quantidade de vagas.",
                        "status": "404",
                    }

                return {"mensagem": "Evento atualizado com sucesso!", "status": "200"}
            except DuplicateKeyError:
                return {"mensagem": "Evento já cadastrado!", "status": "409"}
        else:
            return {"mensagem": self.__validarEvento.errors, "status": "400"}  # type: ignore

    def listarEventos(self) -> dict:
        return {"mensagem": list(self.__colecao.find()), "status": "200"}

    def getEvento(self, idEvento: str) -> dict:
        idEvento = ObjectId(idEvento)
        resultado = self.__colecao.find_one({"_id": idEvento})
        if resultado:
            return {"mensagem": resultado, "status": "200"}
        else:
            return {"mensagem": "Evento não encontrado!", "status": "404"}

    def getEventoID(self, nomeEvento: str) -> dict:
        resultado = self.__colecao.find_one({"nome evento": nomeEvento})
        if resultado:
            return {"mensagem": resultado["_id"], "status": "200"}
        else:
            return {"mensagem": "Evento não encontrado!", "status": "404"}
