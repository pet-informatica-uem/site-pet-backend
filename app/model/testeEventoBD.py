from app.model.eventoBD import EventoBD
from datetime import datetime

evento = {
            "nome evento": 'capacitação python27',
            "resumo": 'evento teste',
            "pré-requisitos": 'nenhum',
            "nível conhecimento": "Não conheço nada",
            "data criação": datetime.now(),
            "data/hora evento": datetime.now(),
            "data inicio inscrição": datetime.now(),
            "data fim inscrição": datetime.now(),
            "local": 'sala 1',
            "vagas ofertadas": {"total vagas": 10, "vagas com notebook": 5, "vagas sem notebook": 5, "vagas preenchidas": 0},
            "carga horária": '5',
            "valor": 10,
            "arte evento": 'images/arteEvento/evento.png',
            "arte qrcode": 'images/arteQRCode/qrcode.png',
            "inscritos": [{"idUsuario": '5f9f9b9b9b9b9b9b9b9b9b9b', "data/hora": datetime.now()}],
            "presentes": [{"idUsuario": '5f9f9b9b9b9b9b9b9b9b9b9b', "data/hora": datetime.now()}],
        }

eventoTeste = EventoBD()
# print(eventoTeste.cadastrarEvento(evento))
# print(eventoTeste.removerEvento('capacitação python6'))
print(eventoTeste.atualizarEvento('capacitação python7', evento))
# print(eventoTeste.buscarEvento('capacitação python27'))
# print(eventoTeste.getInscritos('capacitação python26'))
# print(eventoTeste.pushInscrito('capacitação python26', [{"idUsuario": '222222222b', "data/hora": datetime.now()}]))
# print('\n\n')
# print(eventoTeste.removerInscrito('capacitação python26', "222222222b"))
# print('\n\n')
# print(eventoTeste.getInscritos('capacitação python26'))
