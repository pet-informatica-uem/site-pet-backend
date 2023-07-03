from app.model.inscritosEventoBD import InscritosEventoBD


class InscritosEventoController:
    def __init__(self):
        self.__inscritosEvento = InscritosEventoBD()

    def getInscritosEvento(self, idEvento: str) -> dict:
        inscritosEvento: list = self.__inscritosEvento.getListaInscritos(idEvento)

        if inscritosEvento["status"] == "404":
            return inscritosEvento

        return inscritosEvento