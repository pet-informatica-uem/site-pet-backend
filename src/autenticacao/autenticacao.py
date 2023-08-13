from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hashSenha(senha: str) -> str:
    """
    Recebe uma senha e retorna o seu hash seguro.
    """
    return pwd_context.hash(senha)


def conferirHashSenha(senha: str, hash: str) -> bool:
    """
    Recebe uma senha e seu hash.
    Retorna um bool indicando se o hash corresponde à senha.
    """
    return pwd_context.verify(senha, hash)
