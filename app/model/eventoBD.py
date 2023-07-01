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

        if self.__validarEvento.validate(dadosEvento):
            try:
                resultado = self.__colecao.insert_one(dadosEvento)
                dadosListaInscritos["idEvento"] = resultado.inserted_id
                self.__insctirosEvento.criarListaInscritos(dadosListaInscritos)

                return {"mensagem": "Evento cadastrado com sucesso!", "status": "200"}
            except DuplicateKeyError:
                return {"mensagem": "Evento já cadastrado!", "status": "409"}
        else:
            return {"mensagem": self.__validarEvento.errors, "status": "400"}

    def removerEvento(self, nomeEvento: str) -> dict:
        resultado = self.__colecao.find_one({"nome evento": nomeEvento})
        if resultado:
            self.__insctirosEvento.deletarListaInscritos(resultado["_id"])
            self.__colecao.delete_one({"nome evento": nomeEvento})
            return {"mensagem": "Evento removido com sucesso!", "status": "200"}
        else:
            return {"mensagem": "Evento não encontrado!", "status": "404"}

    def atualizarEvento(self, nomeEvento: str, dadosEvento: object) -> dict:
        if self.getEvento(nomeEvento)["status"] == "404":
            return {"mensagem": "Evento não encontrado!", "status": "404"}

        dadosVagasOfertadas = {
            "vagas ofertadas": dadosEvento.pop("vagas ofertadas"),
        }

        evento = self.__colecao.find_one({"nome evento": nomeEvento})
        dadosEvento["data criação"] = evento["data criação"]

        if self.__validarEvento.validate(dadosEvento):
            try:
                resultado = self.__colecao.update_one(
                    {"nome evento": nomeEvento}, {"$set": dadosEvento}
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
            return {"mensagem": self.__validarEvento.errors, "status": "400"}

    def listarEventos(self) -> dict:
        return {"mensagem": list(self.__colecao.find({}, {"_id": 0})), "status": "200"}

    def getEvento(self, nomeEvento: str) -> dict:
        resultado = self.__colecao.find_one({"nome evento": nomeEvento})
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
