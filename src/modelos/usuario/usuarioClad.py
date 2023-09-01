from pathlib import Path

from pydantic import BaseModel, EmailStr, SecretStr, field_validator

from src.modelos.usuario.validacaoCadastro import ValidacaoCadastro


class UsuarioCriar(BaseModel):
    nome: str
    email: EmailStr
    cpf: str
    senha: SecretStr
    curso: str

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
    nome: str
    email: EmailStr
    curso: str

    foto: Path | None = None
    github: str | None = None
    linkedin: str | None = None
    instagram: str | None = None


class UsuarioLerAdmin(UsuarioLer):
    id: str
    cpf: str

    tipoConta: str
    eventosInscrito: list[tuple[str, bool]] = []


class UsuarioAtualizar(BaseModel):
    nome: str | None = None
    curso: str | None = None
    github: str | None = None
    linkedin: str | None = None
    instagram: str | None = None


class UsuarioAtualizarSenha(BaseModel):
    senha: SecretStr
    novaSenha: SecretStr

    @field_validator("novaSenha")
    def novaSenha_valida(cls, v: SecretStr):
        if not ValidacaoCadastro.senha(v.get_secret_value()):
            raise ValueError("Senha inválida")
        return v


class UsuarioAtualizarEmail(BaseModel):
    senha: SecretStr
    novoEmail: EmailStr

    @field_validator("novoEmail")
    def novoEmail_valido(cls, v: EmailStr):
        if not ValidacaoCadastro.email(v):
            raise ValueError("Email inválido")
        return v


class UsuarioDeletar(BaseModel):
    id: str
