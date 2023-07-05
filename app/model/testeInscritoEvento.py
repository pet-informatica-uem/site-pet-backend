from app.model.inscritosEventoBD import InscritosEventoBD
# from app.model.schema.inscricaoEventoSchema import Inscricao, VagasEvento


inscrito = {
    "idEvento": "648b6a0cef60aa7ee0da482d",
    "idUsuario": "00000000010",
    "nivelConhecimento": "Não conheço nada",
    "tipoInscricao": "com notebook",
    "pagamento": False,
}


inscritos = InscritosEventoBD()
print(inscritos.setInscricao(inscrito))
# print(inscritos.getListaInscritos("6489fcb006b47ec368259532"))
# print(inscritos.setPagamento("6489ff39eb8a09969905edd2", "0000000001"))
# print(inscritos.setPresenca("6489ff39eb8a09969905edd2", "0000000001"))
# print(eventoTeste.getVagas('capacitação python3'))
# print(eventoTeste.setVagas('capacitação python4', 'com notebook'))
# print(eventoTeste.setVagas('capacitação python4', 'sem notebook'))
