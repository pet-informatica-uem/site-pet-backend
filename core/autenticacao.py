from passlib.context import CryptContext

contextoSenha = CryptContext(schemes=["argon2"], deprecated=["auto"])


def conferirHashSenha(senha: str, hash: str):
    return contextoSenha.verify(senha, hash)


def hashSenha(senha: str):
    return contextoSenha.hash(senha)
