from pydantic import BaseModel, EmailStr


class CadastroUsuario(BaseModel):
    email: EmailStr
    senha: str
    confirmacaoSenha: str

    nome: str
    cpf: str


class LoginUsuario(BaseModel):
    email: EmailStr
    senha: str
