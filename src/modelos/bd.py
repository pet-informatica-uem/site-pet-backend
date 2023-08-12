from pymongo import MongoClient
from src.config import config

cliente: MongoClient = MongoClient(str(config.URI_BD))

colecaoTokens = cliente[config.NOME_BD]["authTokens"]
colecaoUsuarios = cliente[config.NOME_BD]["usuarios"]
