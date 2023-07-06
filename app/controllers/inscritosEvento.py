from app.model.inscritosEventoBD import InscritosEventoBD
from app.model.usuarioBD import UsuarioBD


class InscritosEventoController:
    def __init__(self):
        self.__inscritosEvento = InscritosEventoBD()

    def getInscritosEvento(self, idEvento: str) -> dict:
        inscritosEvento: list = self.__inscritosEvento.getListaInscritos(idEvento)

        if inscritosEvento["status"] == "404":
            return inscritosEvento

        # lista de usuários inscritos no evento
        idsUsuarios: list = [
            usuario["idUsuario"] for usuario in inscritosEvento["mensagem"]
        ]
        usuarios: dict = UsuarioBD().getListaUsuarios(idsUsuarios)

        if usuarios["status"] == "404":
            return usuarios

        usuarios: map = list(map(self.__limparUsuarios, usuarios["mensagem"]))
        usuarios = list(usuarios)

        # concatena os dicionarios dos inscritos no evento com o dicionario do usuário, o qual contem nome, email e curso
        [
            inscrito.update(usuario)
            for inscrito, usuario in zip(inscritosEvento["mensagem"], usuarios)
        ]

        return inscritosEvento

    # tirar o _id, cpf, estado da conta, senha, tipo da conta, data criacao
    def __limparUsuarios(self, dadosUsuario: dict) -> dict:
        dadosUsuario.pop("_id")
        dadosUsuario.pop("cpf")
        dadosUsuario.pop("estado da conta")
        dadosUsuario.pop("senha")
        dadosUsuario.pop("tipo conta")
        dadosUsuario.pop("data criacao")

        return dadosUsuario
