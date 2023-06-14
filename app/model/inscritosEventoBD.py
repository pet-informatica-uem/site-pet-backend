from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from datetime import datetime
from bson.objectid import ObjectId
from app.model.validator.dadosEvento import ValidarEvento


class InscritosEventoBD:
    def __init__(self) -> None:
        cliente = MongoClient()
        db = cliente["petBD"]
        self.__colecao = db["inscritos eventos"]
        self.__validarEvento = ValidarEvento().evento()

    def criarListaInscritos(self, idEvento: str) -> dict:
        if self.__colecao.find_one({"idEvento": idEvento}) != None:
            return {"mensagem": "Evento já cadastrado!", "status": "409"}

        self.__colecao.insert_one({"idEvento": idEvento, "inscritos": []})
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

    def getListaInscritos(self, idEvento: str) -> dict:
        idEvento = ObjectId(idEvento)
        resultado = self.__colecao.find_one({"idEvento": idEvento})
        if resultado:
            return {"mensagem": resultado["inscritos"], "status": "200"}
        else:
            return {"mensagem": "Evento não encontrado!", "status": "404"}

    def setInscrito(
        self,
        idEvento: str,
        idUsuario: str,
        nivelConhecimento: str,
        tipoInscricao: str,
    ) -> dict:
        idEvento = ObjectId(idEvento)
        if self.__colecao.find_one({"idEvento": idEvento}) == None:
            return {"mensagem": "Evento não encontrado!", "status": "404"}

        usuariosInscritos = self.__colecao.find_one(
            {"idEvento": idEvento, "inscritos.idUsuario": idUsuario}
        )

        if usuariosInscritos:
            return {"mensagem": "Usuário já inscrito!", "status": "409"}

        self.__colecao.update_one(
            {"idEvento": idEvento},
            {
                "$push": {
                    "inscritos": {
                        "idUsuario": idUsuario,
                        "data/hora": datetime.now(),
                        "pagamento": False,
                        "presente": False,
                        "nível conhecimento": nivelConhecimento,
                        "tipo inscrição": tipoInscricao,
                    }
                }
            },
        )

        return {"mensagem": "Usuário inscrito com sucesso!", "status": "200"}

    def unsetInscrito(self, idEvento: str, idUsuario: str) -> dict:
        idEvento = ObjectId(idEvento)
        resultado = self.__colecao.update_one(
            {"idEvento": idEvento},
            {"$pull": {"inscritos": {"idUsuario": idUsuario}}},
        )

        if resultado.modified_count == 1:
            return {"mensagem": "Usuário removido com sucesso!", "status": "200"}
        else:
            return {"mensagem": "Usuário não encontrado!", "status": "404"}

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
