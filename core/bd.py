from pymongo import MongoClient

from core.config import Settings


def criaConexao():
    conexao = MongoClient(Settings().BD_URL)
    return conexao
