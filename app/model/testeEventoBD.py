from app.model.eventoBD import EventoBD
from datetime import datetime

evento = {
            "nome evento": 'capacitação python26',
            "resumo": 'evento teste',
            "pré-requisitos": 'nenhum',
            "nível conhecimento": "Não conheço nada",
            "data criação": datetime.now(),
            "data/hora evento": datetime.now(),
            "data inicio inscrição": datetime.now(),
            "data fim inscrição": datetime.now(),
            "local": 'sala 1',
            "total vagas ofertadas": '20',
            "laboratorio": "sim",   # isso aqui não está bom, melhorar
            "vagas com notebook": '15',
            "vagas sem notebook": '5',
            "carga horária": '5',
            "pago": "sim",
            "valor": '10',
            "arte evento": b'0010',
            "arte qrcode": b'0010',
            "inscritos": [{"idUsuario": '5f9f9b9b9b9b9b9b9b9b9b9b', "data/hora": datetime.now()}],
            "presentes": [{"idUsuario": '5f9f9b9b9b9b9b9b9b9b9b9b', "data/hora": datetime.now()}],
        }

eventoTeste = EventoBD()
# print(eventoTeste.cadastrarEvento(evento))
# print(eventoTeste.atualizarEvento('capacitação python26', evento))
# print(eventoTeste.buscarEvento('capacitação python27'))
print(eventoTeste.getInscritos('capacitação python26'))
# print(eventoTeste.pushInscrito('capacitação python26', [{"idUsuario": '222222222b', "data/hora": datetime.now()}]))
print('\n\n')
print(eventoTeste.removerInscrito('capacitação python26', "222222222b"))
print('\n\n')
print(eventoTeste.getInscritos('capacitação python26'))
