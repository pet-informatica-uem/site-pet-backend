from app.model.inscritosEventoBD import InscritosEventoBD

# from app.model.schema.inscricaoEventoSchema import Inscricao, VagasEvento


inscrito = {
    "idEvento": "64a7ff34cb7d327cf880af75",
    "idUsuario": "64a74e3787db515fc3f1cba4",
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
