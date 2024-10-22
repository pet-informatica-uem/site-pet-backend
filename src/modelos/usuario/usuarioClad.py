from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, EmailStr, SecretStr, StringConstraints, field_validator

from src.modelos.usuario.usuario import TipoConta
from src.modelos.usuario.validacaoCadastro import ValidacaoCadastro


class UsuarioCriar(BaseModel):
    """""
    Dados de um pedido de criação de um usuário no sistema.
    """
    nome: Annotated[str, StringConstraints(max_length=240)]
    """Nome completo do usuário."""

    email: EmailStr
    """Endereço de e-mail do usuário. O e-mail deve ser válido."""

    cpf: str
    """CPF do usuário. O CPF deve ser válido."""

    senha: SecretStr
    """Senha do usuário. A senha deve obedecer às regras de complexidade."""

    curso: Annotated[str, StringConstraints(max_length=240)]
    """Curso do usuário."""

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
    """
    Dados básicos de um usuário cadastrado no sistema.
    """
    nome: str
    """Nome completo do usuário."""

    email: EmailStr
    """Endereço de e-mail do usuário."""

    curso: str
    """Curso do usuário."""

    github: str | None = None
    """URL do perfil do GitHub do usuário, caso seja petiano."""

    linkedin: str | None = None
    """URL do perfil do LinkedIn do usuário, caso seja petiano."""

    instagram: str | None = None
    """URL do perfil do Instagram do usuário, caso seja petiano."""


class UsuarioLerAdmin(UsuarioLer):
    """
    Dados de um usuário cadastrado no sistema, incluindo informações sensíveis.
    """
    id: str
    """Identificador único do usuário."""

    cpf: str
    """CPF do usuário."""

    emailConfirmado: bool
    """Indica se o e-mail do usuário foi confirmado."""

    tipoConta: TipoConta
    """Tipo de conta do usuário. """

    eventosInscrito: list[str]
    """Lista de identificadores dos eventos nos quais o usuário está inscrito."""

    dataCriacao: datetime
    """Timestamp de criação do usuário."""

    inicioPet: datetime | None = None
    """Timestamp de ingresso no PET, caso seja petiano ou egresso."""

    fimPet: datetime | None = None
    """Timestamp de saída do PET, caso seja petiano ou egresso."""


class UsuarioAtualizar(BaseModel):
    """
    Dados de um pedido de atualização de um usuário no sistema.

    Se um campo for `None`, significa que o campo não será atualizado.
    """
    nome: str | None = None
    """Nome completo do usuário."""

    curso: str | None = None
    """Curso do usuário."""

    github: str | None = None
    """URL do perfil do GitHub do usuário, caso seja petiano."""

    linkedin: str | None = None
    """URL do perfil do LinkedIn do usuário, caso seja petiano."""

    instagram: str | None = None
    """URL do perfil do Instagram do usuário, caso seja petiano."""


class UsuarioAtualizarSenha(BaseModel):
    """
    Dados de um pedido de atualização de senha de um usuário.
    """
    senha: SecretStr
    """Senha atual do usuário."""

    novaSenha: SecretStr
    """Nova senha do usuário. A senha deve obedecer às regras de complexidade."""

    @field_validator("novaSenha")
    def novaSenha_valida(cls, v: SecretStr):
        if not ValidacaoCadastro.senha(v.get_secret_value()):
            raise ValueError("Senha inválida")
        return v


class UsuarioAtualizarEmail(BaseModel):
    """
    Dados de um pedido de atualização do email de um usuário.
    """
    senha: SecretStr
    """Senha do usuário."""

    novoEmail: EmailStr
    """Novo endereço de e-mail do usuário. O e-mail deve ser válido."""

    @field_validator("novoEmail")
    def novoEmail_valido(cls, v: EmailStr):
        if not ValidacaoCadastro.email(v):
            raise ValueError("Email inválido")
        return v


class UsuarioDeletar(BaseModel):
    """"
    Dados de um pedido de remoção de um usuário no sistema.
    """
    id: str
    """Identificador único do usuário a ser removido."""
