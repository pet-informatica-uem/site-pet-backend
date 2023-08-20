from datetime import datetime

from src.modelos.bd import EventoBD, InscritoBD, UsuarioBD, colecaoEventos
from src.modelos.evento.evento import Evento
from src.modelos.inscrito.inscrito import Inscrito
from src.modelos.usuario.usuario import Usuario


def verificaEventosFinalizados():
    # Recupera eventos ativos
    eventos: list[Evento] = [Evento(**e) for e in colecaoEventos.find({"ativo": True})]

    for evento in eventos:
        # Verifica se o último dia do evento já passou
        if evento.dias[-1][-1] < datetime.now():
            # Desativa o evento
            evento.ativo = False
            EventoBD.atualizar(evento)

            # Recupera inscritos
            inscritos: list[Inscrito] = InscritoBD.listarInscritosEvento(evento.id)
            for inscrito in inscritos:
                # Recupera usuário
                usuario: Usuario = UsuarioBD.buscar("_id", inscrito.idUsuario)

                # Atualiza inscrição para inativa
                usuario.eventosInscrito.remove((evento.id, True))
                usuario.eventosInscrito.append((evento.id, False))
