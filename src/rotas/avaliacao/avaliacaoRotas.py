"""
Rotas relacionadas ao modulo de avaliacao de eventos.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, status

from src.modelos.avaliacao.avaliacao import (
    FormularioAvaliacaoEvento,
    ResultadoAvaliacaoEvento,
    SubmissaoAvaliacaoAnonima,
)
from src.modelos.avaliacao.avaliacaoClad import (
    ConfiguracaoFormularioCriar,
    SubmissaoAvaliacaoCriar,
)
from src.modelos.usuario.usuario import Usuario
from src.rotas.avaliacao.avaliacaoControlador import AvaliacaoControlador
from src.rotas.usuario.usuarioRotas import getPetianoAutenticado, getUsuarioAutenticado

roteador: APIRouter = APIRouter(
    prefix="/eventos/{idEvento}/avaliacao",
    tags=["Avaliacao"],
)

@roteador.put(
    "/formulario",
    name="Configurar formulario de avaliacao",
    description="Cria ou atualiza o formulario de avaliacao de um evento.",
    status_code=status.HTTP_200_OK,
    response_model=FormularioAvaliacaoEvento,
)
def configurarFormulario(
    idEvento: str,
    dadosFormulario: ConfiguracaoFormularioCriar,
    usuario: Annotated[Usuario, Depends(getPetianoAutenticado)],
):
    """
    Cria ou atualiza o formulario de avaliacao de um evento.

    :param idEvento: Identificador unico do evento.
    :param dadosFormulario: Configuracao do formulario de avaliacao.
    :param usuario: Usuario autenticado (petiano).
    :return formulario: Formulario criado ou atualizado.
    """
    return AvaliacaoControlador.configurarFormulario(idEvento, dadosFormulario)


@roteador.post(
    "/submissoes",
    name="Enviar formulario de avaliacao",
    description="Envia uma submissao anonima de avaliacao para um evento.",
    status_code=status.HTTP_201_CREATED,
    response_model=SubmissaoAvaliacaoAnonima,
)
def enviarFormulario(
    idEvento: str,
    submissao: SubmissaoAvaliacaoCriar,
    usuario: Annotated[Usuario, Depends(getUsuarioAutenticado)],
):
    """
    Envia uma avaliacao para um formulario de evento.

    :param idEvento: Identificador unico do evento.
    :param submissao: Respostas submetidas pelo usuario.
    :param usuario: Usuario autenticado que enviara a avaliacao.
    :return submissao: Submissao anonima registrada.
    """
    return AvaliacaoControlador.enviarFormulario(idEvento, usuario.id, submissao)


@roteador.get(
    "/formulario",
    name="Obter formulario de avaliacao",
    description="Recupera o formulario de avaliacao de um evento.",
    status_code=status.HTTP_200_OK,
    response_model=FormularioAvaliacaoEvento,
)
def obterFormulario(
    idEvento: str,
    usuario: Annotated[Usuario, Depends(getUsuarioAutenticado)],
):
    """
    Recupera o formulario de avaliacao de um evento.

    :param idEvento: Identificador unico do evento.
    :param usuario: Usuario autenticado.
    :return formulario: Formulario de avaliacao do evento.
    """
    return AvaliacaoControlador.obterFormulario(idEvento)


@roteador.get(
    "/submissoes/{idSubmissao}",
    name="Obter submissao de avaliacao",
    description="Recupera uma submissao anonima de avaliacao enviada para o evento.",
    status_code=status.HTTP_200_OK,
    response_model=SubmissaoAvaliacaoAnonima,
)
def obterRespostaFormulario(
    idEvento: str,
    idSubmissao: str,
    usuario: Annotated[Usuario, Depends(getPetianoAutenticado)],
):
    """
    Recupera uma submissao anonima especifica de um evento.

    :param idEvento: Identificador unico do evento.
    :param idSubmissao: Identificador unico da submissao.
    :param usuario: Usuario autenticado (petiano).
    :return submissao: Submissao anonima encontrada.
    """
    return AvaliacaoControlador.obterRespostaFormulario(idEvento, idSubmissao)


@roteador.get(
    "/resultados",
    name="Obter resultados da avaliacao",
    description="Recupera a visao geral consolidada de resultados do formulario.",
    status_code=status.HTTP_200_OK,
    response_model=ResultadoAvaliacaoEvento,
)
def obterResultados(
    idEvento: str,
    usuario: Annotated[Usuario, Depends(getPetianoAutenticado)],
):
    """
    Recupera os resultados consolidados da avaliacao de um evento.

    :param idEvento: Identificador unico do evento.
    :param usuario: Usuario autenticado (petiano).
    :return resultado: Resultado consolidado da avaliacao.
    """
    return AvaliacaoControlador.obterResultados(idEvento)
