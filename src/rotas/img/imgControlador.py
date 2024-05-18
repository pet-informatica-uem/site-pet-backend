from pathlib import Path

from fastapi.responses import FileResponse

from src.modelos.excecao import NaoEncontradoExcecao
from src.rotas.evento.eventoControlador import EventoControlador
from src.rotas.inscrito.inscritoControlador import InscritosControlador
from src.rotas.usuario.usuarioControlador import UsuarioControlador


def getFileResponse(caminho: str | None):
    if caminho and caminho != "" and Path(caminho).exists():
        return FileResponse(caminho)

    raise NaoEncontradoExcecao(message="A imagem não foi encontrada")


class ImagemControlador:
    @staticmethod
    def getImagemUsuario(id: str):
        usuario = UsuarioControlador.getUsuario(id)

        return getFileResponse(usuario.foto)

    @staticmethod
    def getImagemEvento(id: str):
        evento = EventoControlador.getEvento(id)

        return getFileResponse(evento.arte)

    @staticmethod
    def getCrachaEvento(id: str):
        evento = EventoControlador.getEvento(id)

        return getFileResponse(evento.cracha)

    @staticmethod
    def getComprovanteInscrito(idEvento: str, idInscrito: str):
        inscrito = InscritosControlador.getInscrito(idEvento, idInscrito)

        return getFileResponse(inscrito.comprovante)
