import logging
from datetime import datetime

from bson.objectid import ObjectId
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

from src.modelos.evento.dadosEvento import ValidarEvento
from src.modelos.evento.inscritosEventoBD import InscritosEventoBD
from src.modelos.excecao import JaExisteExcecao, NaoEncontradoExcecao, NaoAtualizadaExcecao

class EventoBD:
    def __init__(self) -> None:
        cliente = MongoClient()
        db = cliente["petBD"]
        self.__colecao = db["eventos"]
        self.__validarEvento = ValidarEvento().evento()
        self.__insctirosEvento = InscritosEventoBD()

    def cadastrarEvento(self, dadosEvento: dict) -> str:
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
                return resultado.inserted_id
            except DuplicateKeyError:
                logging.warning("Evento já cadastrado!")
                raise JaExisteExcecao(message="Evento já cadastrado!")
        else:
            raise Exception(self.__validarEvento.errors)  # type: ignore

    def removerEvento(self, idEvento: str) -> bool:
        idEvento :ObjectId = ObjectId(idEvento)
        resultado = self.__colecao.find_one({"_id": idEvento})
        if resultado:
            self.__insctirosEvento.deletarListaInscritos(resultado["_id"])
            self.__colecao.delete_one({"_id": idEvento})
            return True
        else:
            return NaoEncontradoExcecao(messege = "Evento não encontrado. ")

    def atualizarEvento(self, idEvento: str, dadosEvento: object) -> ObjectId:
        idEvento :ObjectId = ObjectId(idEvento)

        dadosVagasOfertadas :dict = dadosEvento.pop("vagas ofertadas")

        evento :dict = self.__colecao.find_one({"_id": idEvento})
        dadosEvento["data criação"] :dict = evento["data criação"]  

        if self.__validarEvento.validate(dadosEvento):  # type: ignore
            try: 
                self.__colecao.update_one(
                    {"_id": idEvento}, {"$set": dadosEvento}
                )
                
                idEvento :ObjectId = self.__insctirosEvento.atualizarVagasOfertadas(
                    evento["_id"], dadosVagasOfertadas
                )

                return idEvento
            except DuplicateKeyError:
                raise JaExisteExcecao("Evento já cadastrado! ")
        else:
            raise Exception(self.__validarEvento.errors)  # type: ignore

    def listarEventos(self) -> list:
        return list(self.__colecao.find())

    def getEvento(self, idEvento: str) -> dict:   #AQUI TA ERRADO, AQUI É getEvento O outro É PELO NOME.
        idEvento = ObjectId(idEvento)
        resultado = self.__colecao.find_one({"_id": idEvento})
        if resultado:
            return resultado
        else:
            raise NaoEncontradoExcecao(messege = "Evento não encontrado!")

    def getEventoID(self, nomeEvento: str) -> str:
        resultado = self.__colecao.find_one({"nome evento": nomeEvento})
        if resultado:
            return resultado["_id"]
        else:
            raise NaoEncontradoExcecao(messege = "Evento não encontrado!")
