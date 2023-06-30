from datetime import date, datetime
from enum import Enum
from pathlib import Path
from typing import Self
from pydantic import BaseModel, EmailStr, HttpUrl


class EstadoConta(str, Enum):
    """
    Enumeração que representa o estado da conta.
    """

    ATIVO = "ativo"
    "A conta está ativada e possui email confirmado."

    INATIVO = "inativo"
    "A conta está desativada, pendente de confirmação."


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
    Classe representando um usuário do sistema.
    """

    id: str
    "Identificador único."

    email: EmailStr
    "Endereço de email do usuário."

    estadoConta: EstadoConta
    "Estado da conta. Indica se o usuário teve seu email confirmado ou não."

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

    def paraBd(self) -> dict:
        d = {
            "_id": self.id,
            "nome": self.nome,
            "email": self.email,
            "cpf": self.cpf,
            "curso": self.curso or "",
            "estado da conta": self.estadoConta,
            "tipo conta": self.tipoConta,
            "data criacao": self.criado,
            "tempo de pet": {
                "data inicio": self.inicioPet,
                "data fim": self.fimPet,
            },
            "redes sociais": {
                "github": self.github,
                "linkedin": self.linkedin,
                "instagram": self.instagram,
                "twitter": self.twitter,
            },
            "foto perfil": self.foto,
        }

        if not (self.inicioPet or self.fimPet):
            d.pop("tempo de pet")

        if not (self.foto):
            d.pop("foto perfil")

        if not (self.github or self.linkedin or self.instagram or self.twitter):
            d.pop("redes sociais")

        return d

    @classmethod
    def deBd(cls, repr: dict) -> Self:
        """
        Converte a representação do banco de dados para um
        objeto deste tipo.
        """
        dados = {
            "id": str(repr.get("_id")),
            "nome": repr.get("nome"),
            "email": repr.get("email"),
            "cpf": repr.get("cpf"),
            "curso": repr.get("curso"),
            "estadoConta": repr.get("estado da conta"),
            "tipoConta": repr.get("tipo conta"),
            "criado": repr.get("data criacao"),
            "foto": repr.get("foto perfil"),
        }

        if tempo := repr.get("tempo de pet"):
            dados.update(
                {"inicioPet": tempo.get("data inicio"), "fimPet": tempo.get("data fim")}
            )

        if redes := repr.get("redes sociais"):
            dados.update(
                {
                    "github": redes.get("github"),
                    "linkedin": redes.get("linkedin"),
                    "instagram": redes.get("instagram"),
                    "twitter": redes.get("twitter"),
                }
            )

        return cls(**dados)


class UsuarioSenha(Usuario):
    """
    Classe que representa o usuário do sistema, contendo hash da senha.
    """

    senha: str
    "Hash da senha do usuário."

    def paraBd(self) -> dict:
        d = super().paraBd()
        d.update({"senha": self.senha})
        return d

    @classmethod
    def deBd(cls, repr):
        u = Usuario.deBd(repr)
        u = u.dict()
        u.update({"senha": repr.get("senha")})
        return cls(**u)
