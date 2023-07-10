from datetime import datetime

from app.model.eventoBD import EventoBD

evento = {
    "nome evento": "capacitação python9",
    "resumo": "evento teste",
    "pré-requisitos": "nenhum",
    "data/hora evento": datetime.now(),
    "data inicio inscrição": datetime.now(),
    "data fim inscrição": datetime.now(),
    "local": "sala 1",
    "vagas ofertadas": {"vagas com notebook": 20, "vagas sem notebook": 50},
    "carga horária": "7",
    "valor": 10,
    "arte evento": "images/arteEvento/evento.png",
    "arte qrcode": "images/arteQRCode/qrcode.png",
}

eventoTeste = EventoBD()
print(eventoTeste.cadastrarEvento(evento))
# print(eventoTeste.removerEvento('capacitação python7'))
# print(eventoTeste.listarEventos())
# print(eventoTeste.atualizarEvento("capacitação python5", evento))
# print(eventoTeste.getEvento('capacitação python2'))
# print(eventoTeste.getEventoId('capacitação python'))
