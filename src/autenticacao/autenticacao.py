"""
Funções auxiliares para autenticação de usuários.
"""

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hashSenha(senha: str) -> str:
    """
    Recebe uma senha e retorna o seu hash seguro.

    :param senha: Senha a ser hasheada.
    :return hash: Hash da senha.
    """
    return pwd_context.hash(senha)


def conferirHashSenha(senha: str, hash: str) -> bool:
    """
    Recebe uma senha e seu hash.
    Retorna um bool indicando se o hash corresponde à senha.

    :param senha: Senha a ser verificada.
    :param hash: Hash da senha.

    :return valida: True se o hash corresponder à senha, False caso contrário.
    """
    return pwd_context.verify(senha, hash)
