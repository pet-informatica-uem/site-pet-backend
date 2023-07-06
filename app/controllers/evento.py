from app.model.eventoBD import EventoBD


class EventoController:
    def __init__(self):
        self.__evento = EventoBD()

    def listarEventos(self) -> dict:
        eventos: dict = self.__evento.listarEventos()

        if eventos["status"] == "404":
            return eventos
        
        for evento in eventos['mensagem']:
            evento["_id"] = str(evento["_id"])

        return eventos
