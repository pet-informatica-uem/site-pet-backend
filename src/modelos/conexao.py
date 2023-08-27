from pymongo import MongoClient
from src.config import config

class ConexaoBD:
    def __init__(self, nomeBanco: str = config.NOME_BD) -> None:
        print('\n\n|||||||||||||||||\n\n')
        print(nomeBanco)
        
        self.cliente = MongoClient(str(config.URI_BD))
        self.colecaoTokens = self.cliente[nomeBanco]["authTokens"]
        self.colecaoUsuarios = self.cliente[nomeBanco]["usuarios"]
        self.colecaoUsuarios.create_index("email", unique=True)
        self.colecaoUsuarios.create_index("cpf", unique=True)
        self.colecaoEventos = self.cliente[nomeBanco]["eventos"]
        self.colecaoInscritos = self.cliente[nomeBanco]["inscritos"]
        self.colecaoInscritos.create_index(
            [("idEvento", 1), ("idUsuario", 1)], unique=True
        )
