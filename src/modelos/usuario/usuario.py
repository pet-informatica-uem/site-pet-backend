from datetime import date, datetime
from enum import Enum
from pathlib import Path

from pydantic import BaseModel, EmailStr, HttpUrl


class TipoConta(str, Enum):
    """
    Tipo de conta de usuário. Tipos diferentes possuem permissões diferentes.
    """

    ESTUDANTE = "estudante"
    "Conta base. Pode visualizar dados e se inscrever em eventos e atividades."

    EGRESSO = "petiano egresso"
    "Conta pertencente a um ex-petiano. Possui as mesmas permissões de um estudante."

    PETIANO = "petiano"
    "Conta pertencente a um petiano ativo. Possui permissões totais."


class Usuario(BaseModel):
    """
    Classe que representa um usuário do sistema.
    """

    id: str
    "Identificador único."

    email: EmailStr
    "Endereço de email do usuário."

    senha: str
    "Hash da senha do usuário."

    emailConfirmado: bool
    "Estado da confirmação do email. Indica se o usuário teve seu email confirmado ou não."

    cpf: str
    "CPF do usuário."

    nome: str
    "Nome completo do usuário."

    curso: str | None
    "Curso do usuário."

    tipoConta: TipoConta
    "Tipo de conta. Representa permissões."

    criado: datetime
    "Data e hora de criação da conta."

    # campos exclusivos para petianos

    inicioPet: date | None
    "Data de ingresso no PET-Informática."

    fimPet: date | None
    "Data de desligamento do PET-Informática."

    github: HttpUrl | None
    "Link para o Github pessoal."

    linkedin: HttpUrl | None
    "Link para o LinkedIn pessoal."

    instagram: HttpUrl | None
    "Link para o Instagram pessoal."

    twitter: HttpUrl | None
    "Link para o Twitter pessoal."

    foto: Path | None
    "Caminho para foto de perfil do petiano."
