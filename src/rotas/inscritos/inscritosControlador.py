

from datetime import datetime
from modelos.inscritos.inscrito import Inscrito, InscritoCriar


class InscritosControlador:
    @staticmethod
    def cadastrarInscrito(idEvento: str, idInscrito: str, inscrito: InscritoCriar):

        d = {
            "idEvento": idEvento,
            "idUsuario": idInscrito,
            "dataHora": datetime.now(),
        }

        d.update(**inscrito.model_dump())
        d = Inscrito(**d)

        