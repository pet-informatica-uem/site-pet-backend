


from modelos.evento.inscritosEventoBD import InscritosEventoBD
from modelos.usuario.usuarioBD import UsuarioBD


class InscritosEventoController:
    def __init__(self):
        self.__inscritosEvento = InscritosEventoBD()

    def getInscritosEvento(self, idEvento: str) -> dict:
        inscritosEvento: list = self.__inscritosEvento.getListaInscritos(idEvento) # type: ignore

        if inscritosEvento["status"] == "404": # type: ignore
            return inscritosEvento # type: ignore

        # lista de usuários inscritos no evento
        idsUsuarios: list = [
            usuario["idUsuario"] for usuario in inscritosEvento["mensagem"] # type: ignore
        ]
        usuarios: dict = UsuarioBD().getListaUsuarios(idsUsuarios) # type: ignore

        if usuarios["status"] == "404":
            return usuarios

        usuarios: map = list(map(self.__limparUsuarios, usuarios["mensagem"])) # type: ignore
        usuarios = list(usuarios) # type: ignore

        # concatena os dicionarios dos inscritos no evento com o dicionario do usuário, o qual contem nome, email e curso
        for inscrito, usuario in zip(inscritosEvento["mensagem"], usuarios): # type: ignore
            inscrito['idUsuario'] = str(inscrito['idUsuario'])
            inscrito.update(usuario)

        return inscritosEvento # type: ignore

    # tirar o _id, cpf, estado da conta, senha, tipo da conta, data criacao
    def __limparUsuarios(self, dadosUsuario: dict) -> dict:
        dadosUsuario.pop("_id")
        dadosUsuario.pop("cpf")
        dadosUsuario.pop("estado da conta")
        dadosUsuario.pop("senha")
        dadosUsuario.pop("tipo conta")
        dadosUsuario.pop("data criacao")

        return dadosUsuario
