from app.models.eventoBD import EventoBD

evento = {
    "nome evento": "teste",
    "resumo": "teste",
    "pré-requisitos": "teste",
    "nível conhecimento": "Não conheço nada",
    "data criação": "2021-10-10 10:10:10",
    "data evento": "2021-10-10 10:10:10",
    "hora evento": "10:10",
    "data inicio inscrição": "2021-10-10 10:10:10",
    "data fim inscrição": "2021-10-10 10:10:10",
    "local": "teste",
    "total vagas ofertadas": "10",
    "laboratorio": "sim",
    "vagas com notebook": "5",
    "vagas sem notebook": "5",
    "carga horária": "10",
    "pago": "sim",
    "valor": "10",
    "arte evento": "teste",
    "qr code": "sim",
    "arte qrcode": "teste",
    "inscritos": [
        {
            "idUsuario": "6161f1b7e3b6b3b3f0b3b3b3",
            "data": "2021-10-10 10:10:10",
            "hora": "10:10",
}
    ],
    "presentes": [
        {
            "idUsuario": "6161f1b7e3b6b3b3f0b3b3b3",
            "data": "2021-10-10 10:10:10",
            "hora": "10:10",
}
    ],
}

eventoTeste = EventoBD()
# eventoTeste.cadastrarEvento(evento)
