from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, EmailStr, SecretStr, StringConstraints, field_validator

from src.modelos.usuario.validacaoCadastro import ValidacaoCadastro


class UsuarioCriar(BaseModel):
    """""
    Classe que valida o email, cpf e senha do usuário.
        :EmailStr é uma função do pydantic que valida o email
        :SecretStr é uma função do pydantic que encripta a senha
        :StringConstraints é uma função do pydantic que valida o tamanho da string
        :@field_validator("campo") é um decorador do pydantic que valida o campo
    """
    nome: Annotated[str, StringConstraints(max_length=240)]
    email: EmailStr
    cpf: str
    senha: SecretStr
    curso: Annotated[str, StringConstraints(max_length=240)]

    @field_validator("cpf")
    def cpf_valido(cls, v: str):
        if not ValidacaoCadastro.cpf(v):
            raise ValueError("CPF inválido")
        return v

    @field_validator("email")
    def email_valido(cls, v: EmailStr):
        if not ValidacaoCadastro.email(v):
            raise ValueError("Email inválido")
        return v

    @field_validator("senha")
    def senha_valida(cls, v: SecretStr):
        if not ValidacaoCadastro.senha(v.get_secret_value()):
            raise ValueError("Senha inválida")
        return v


class UsuarioLer(BaseModel):
    """"
    Classe que representa um usuário no sistema
    """
    nome: str
    email: EmailStr
    curso: str

    foto: str | None = None
    github: str | None = None
    linkedin: str | None = None
    instagram: str | None = None


class UsuarioLerAdmin(UsuarioLer):
    """"
    Classe que representa um usuário no sistema, com informações adicionais para administrador
    """
    id: str
    cpf: str
    emailConfirmado: bool
    tipoConta: str
    eventosInscrito: list[str]
    dataCriacao: datetime
    inicioPet: datetime | None = None
    fimPet: datetime | None = None


class UsuarioAtualizar(BaseModel):
    """"
    Classe usada para atualizar um usuário
    """
    nome: str | None = None
    curso: str | None = None
    github: str | None = None
    linkedin: str | None = None
    instagram: str | None = None


class UsuarioAtualizarSenha(BaseModel):
    """"
    Classe usada para atualizar a senha de um usuário
        :senhaStr é uma função do pydantic que encripta a senha
    """
    senha: SecretStr
    novaSenha: SecretStr

    @field_validator("novaSenha")
    def novaSenha_valida(cls, v: SecretStr):
        if not ValidacaoCadastro.senha(v.get_secret_value()):
            raise ValueError("Senha inválida")
        return v


class UsuarioAtualizarEmail(BaseModel):
    """""
    Classe usada para atualizar o email de um usuário
        :EmailStr é uma função do pydantic que valida o email
        :senhaStr é uma função do pydantic que encripta a senha
    """
    senha: SecretStr
    novoEmail: EmailStr

    @field_validator("novoEmail")
    def novoEmail_valido(cls, v: EmailStr):
        if not ValidacaoCadastro.email(v):
            raise ValueError("Email inválido")
        return v


class UsuarioDeletar(BaseModel):
    """"
    Classe usada para deletar um usuário
    """
    id: str
