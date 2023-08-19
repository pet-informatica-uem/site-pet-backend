from pathlib import Path

from pydantic import BaseModel


class Petiano(BaseModel):
    nome: str
    github: str | None = None
    linkedin: str | None = None
    instagram: str | None = None
    foto: Path | None = None
