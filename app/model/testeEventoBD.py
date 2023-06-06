from app.model.eventoBD import EventoBD
from datetime import datetime

evento = {
            "nome evento": 'capacitação python5',
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
            "inscritos": [],
            "presentes": [],
        }

eventoTeste = EventoBD()
# print(eventoTeste.cadastrarEvento(evento))  
# print(eventoTeste.removerEvento('capacitação python29'))
# print(eventoTeste.listarEventos())
# print(eventoTeste.atualizarEvento('capacitação python18', evento))
# print(eventoTeste.getEvento('capacitação python18'))
# print(eventoTeste.addInscrito('capacitação python5', '0000000004', False))
# print(eventoTeste.setPagamento('capacitação python5', '0000000002', True))
# print(eventoTeste.removerInscrito('capacitação python2', '0000000002'))
# print(eventoTeste.addPresente('capacitação python5', '0000000009'))
# print(eventoTeste.removerPresente('capacitação python3', '0000000002'))
