from app.model.inscritosEventoBD import InscritosEventoBD
from app.model.eventoBD import EventoBD
from datetime import datetime



inscritos = InscritosEventoBD()
# print(inscritos.setInscrito("6489ff39eb8a09969905edd2", "0000000004", "Não conheço nada", "vaga com notebook"))
# print(inscritos.getListaInscritos("6489fcb006b47ec368259532"))
# print(inscritos.unsetInscrito("6489dc80cd84cfa9d7a9acf6", "0000000004"))
# print(inscritos.setPagamento("6489ff39eb8a09969905edd2", "0000000001"))
print(inscritos.setPresenca("6489ff39eb8a09969905edd2", "0000000001"))