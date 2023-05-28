from pydantic import BaseModel


class Usuario(BaseModel):
    nome: str
    cpf: str
    email: str
    emailValidado: bool


class UsuarioBd(Usuario):
    senha: str
