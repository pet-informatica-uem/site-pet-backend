from pathlib import Path

from pydantic import BaseModel

from src.modelos.usuario.usuario import TipoConta, Usuario
from src.modelos.bd import colecaoUsuarios


class Petiano(BaseModel):
    nome: str
    github: str | None = None
    linkedin: str | None = None
    instagram: str | None = None
    foto: Path | None = None


def infoPetianos() -> list[Petiano]:
    petianos = [
        Usuario(**u) for u in colecaoUsuarios.find({"tipoConta": TipoConta.PETIANO})
    ]
    infoPetianos: list[Petiano] = []

    for petiano in petianos:
        infoPetianos.append(
            Petiano(
                nome=petiano.nome,
                github=petiano.github,
                linkedin=petiano.linkedin,
                instagram=petiano.instagram,
            )
        )

    return infoPetianos
