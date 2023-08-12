from src.modelos.usuario.usuarioBD import UsuarioBD


def infoPetianos() -> list:
    petianos = UsuarioBD().getListaPetianos()
    infoPetianos = []

    for petiano in petianos:
        infoPetianos.append(
            {
                "nome": petiano.get("nome"),
                "redes sociais": petiano.get("redes sociais"),
                "foto perfil": petiano.get("foto perfil"),
            }
        )

    return infoPetianos
