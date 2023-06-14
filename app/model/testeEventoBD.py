from app.model.eventoBD import EventoBD
from datetime import datetime

evento = {
            "nome evento": 'capacitação python12',
            "resumo": 'evento teste',
            "pré-requisitos": 'nenhum',
            "data/hora evento": datetime.now(),
            "data inicio inscrição": datetime.now(),
            "data fim inscrição": datetime.now(),
            "local": 'sala 1',
            "vagas ofertadas": {"vagas com notebook": 9, "vagas sem notebook": 5},
            "carga horária": '7',
            "valor": 10,
            "arte evento": 'images/arteEvento/evento.png',
            "arte qrcode": 'images/arteQRCode/qrcode.png',
        }

eventoTeste = EventoBD()
print(eventoTeste.cadastrarEvento(evento))  
# print(eventoTeste.removerEvento('capacitação python7'))
# print(eventoTeste.listarEventos())
# print(eventoTeste.atualizarEvento('capacitação python', evento))
# print(eventoTeste.getEvento('capacitação python2'))
# print(eventoTeste.getEventoId('capacitação python'))
# print(eventoTeste.getVagas('capacitação python3'))
# print(eventoTeste.setVagas('capacitação python4', 'com notebook'))
# print(eventoTeste.setVagas('capacitação python4', 'sem notebook'))
