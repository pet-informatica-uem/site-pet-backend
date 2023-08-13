from typing import Annotated
from fastapi import UploadFile
from pydantic import BaseModel, EmailStr, HttpUrl, SecretStr, field_validator

from src.modelos.usuario.validacaoCadastro import ValidacaoCadastro


class UsuarioCriar(BaseModel):
    nome: str
    email: EmailStr
    cpf: str
    senha: SecretStr
    curso: str

    @field_validator("cpf")
    def cpf_valido(cls, v):
        if not ValidacaoCadastro.cpf(v):
            raise ValueError("CPF inválido")
        return v

    @field_validator("email")
    def email_valido(cls, v):
        if not ValidacaoCadastro.email(v):
            raise ValueError("Email inválido")
        return v

    @field_validator("senha")
    def senha_valida(cls, v):
        if not ValidacaoCadastro.senha(v.get_secret_value()):
            raise ValueError("Senha inválida")
        return v


class UsuarioLer(BaseModel):
    id: str
    nome: str
    email: EmailStr
    cpf: str
    curso: str
    tipoConta: str


class UsuarioAtualizar(BaseModel):
    nome: str | None = None
    curso: str | None = None
    github: HttpUrl | None = None
    linkedin: HttpUrl | None = None
    instagram: HttpUrl | None = None


class UsuarioAtualizarSenha(BaseModel):
    senha: SecretStr
    novaSenha: SecretStr

    @field_validator("novaSenha")
    def novaSenha_valida(cls, v):
        if not ValidacaoCadastro.senha(v):
            raise ValueError("Senha inválida")
        return v
    

class UsuarioAtualizarEmail(BaseModel):
    senha: SecretStr
    novoEmail: EmailStr

    @field_validator("novoEmail")
    def novoEmail_valido(cls, v):
        if not ValidacaoCadastro.email(v):
            raise ValueError("Email inválido")
        return v
    

class UsuarioDeletar(BaseModel):
    id: str
