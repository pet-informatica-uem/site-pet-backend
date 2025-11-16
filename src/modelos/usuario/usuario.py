"""
Modelos de dados relacionados a usuários do sistema.
"""

from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, EmailStr, Field


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

class EventosInscrito(BaseModel):
    """
    Classe que representa um evento no qual o petiano está inscrito.
    """
    
    titulo: str
    "Título do evento."

    arte: str | None = None
    "Caminho para a arte do evento."


class Usuario(BaseModel):
    """
    Classe que representa um usuário do sistema.
    """

    id: str = Field(..., alias="_id")
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

    curso: str | None = None
    "Curso do usuário."

    tipoConta: TipoConta
    "Tipo de conta. Representa permissões."

    eventosInscrito: list[str] = []
    "Lista de tuplas de id de evento."

    dataCriacao: datetime
    "Data e hora de criação da conta."

    # campos exclusivos para petianos

    inicioPet: date | None = None
    "Data de ingresso no PET-Informática."

    fimPet: date | None = None
    "Data de desligamento do PET-Informática."

    github: str | None = None
    "Link para o Github pessoal."

    linkedin: str | None = None
    "Link para o LinkedIn pessoal."

    instagram: str | None = None
    "Link para o Instagram pessoal."

    twitter: str | None = None
    "Link para o Twitter pessoal."

    foto: str | None = None
    "Caminho para foto de perfil do petiano."

    sobre: str | None = None
    "Descrição pessoal do petiano."

    apadrinhadoPor: str | None = None
    "Id do petiano que apadrinhou este petiano."

class Petiano(BaseModel):
    """
    Subconjunto dos dados de um usuário específico para a visualização de petianos.
    """
    id: str
    "Identificador único."

    nome: str
    "Nome completo do usuário."

    github: str | None = None
    "Link para o Github pessoal."

    linkedin: str | None = None
    "Link para o LinkedIn pessoal."

    instagram: str | None = None
    "Link para o Instagram pessoal."

    foto: str | None = None
    "Caminho para foto de perfil do petiano."

    sobre: str | None = None
    "Descrição pessoal do petiano."

    inicioPet: date | None = None
    "Data de ingresso no PET-Informática."

    fimPet: date | None = None
    "Data de desligamento do PET-Informática."

    tipoConta: TipoConta | None = None
    "Tipo de conta. Representa petianos ou egressos"

    eventosInscrito: list[EventosInscrito] = []
    "Lista de objetos que representam os eventos que o petiano participou."

    apadrinhadoPor: str | None = None
    "Id do petiano que apadrinhou este petiano."
