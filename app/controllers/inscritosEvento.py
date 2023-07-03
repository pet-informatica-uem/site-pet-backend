from app.model.inscritosEventoBD import InscritosEventoBD
from app.model.usuarioBD import UsuarioBD


class InscritosEventoController:
    def __init__(self):
        self.__inscritosEvento = InscritosEventoBD()

    def getInscritosEvento(self, idEvento: str) -> dict:
        inscritosEvento: list = self.__inscritosEvento.getListaInscritos(idEvento)

        if inscritosEvento["status"] == "404":
            return inscritosEvento
        
        # UsuarioBD()

        return inscritosEvento