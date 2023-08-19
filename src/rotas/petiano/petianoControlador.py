from src.rotas.petiano.petianoClad import Petiano
from src.modelos.bd import listar


def infoPetianos() -> list[Petiano]:
    petianos = listar(Petiano)
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
