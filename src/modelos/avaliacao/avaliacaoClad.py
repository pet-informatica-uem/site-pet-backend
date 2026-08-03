"""
Modelos de entrada e saida para operacoes de avaliacao (CLAD: Create, List, Atualizar, Delete).
"""

from datetime import datetime

from pydantic import BaseModel, Field, model_validator

from src.modelos.avaliacao.avaliacao import RespostaPerguntaAvaliacao, SecaoAvaliacao, TipoPerguntaAvaliacao


class PerguntaDinamicaCriar(BaseModel):
    """
    Dados para criacao de uma pergunta dinamica pelo organizador.
    """

    texto: str
    "Enunciado da pergunta."

    tipo: TipoPerguntaAvaliacao
    "Tipo da pergunta."

    obrigatoria: bool = True
    "Indica se a pergunta deve obrigatoriamente ser respondida."

    opcoes: list[str] | None = None
    "Lista de opcoes para perguntas de multipla escolha ou caixas de selecao."

    @model_validator(mode="after")
    def validar_pergunta_dinamica(self):
        """
        Valida regras especificas para perguntas dinamicas.
        """
        if self.tipo == TipoPerguntaAvaliacao.ESCALA_UM_A_CINCO:
            raise ValueError("Perguntas dinamicas nao suportam escala de 1 a 5.")

        if self.tipo in (TipoPerguntaAvaliacao.MULTIPLA_ESCOLHA, TipoPerguntaAvaliacao.CAIXAS_DE_SELECAO):
            if not self.opcoes:
                raise ValueError("Perguntas de escolha exigem ao menos uma opcao.")
            self.opcoes = [o.strip() for o in self.opcoes if o.strip()]
            if not self.opcoes:
                raise ValueError("Opcoes nao podem ser vazias.")
        elif self.opcoes:
            raise ValueError("Opcoes permitidas apenas para perguntas de escolha.")

        return self


class ConfiguracaoFormularioCriar(BaseModel):
    """
    Dados para configuracao ou atualizacao do formulario de avaliacao de um evento.
    """

    liberarApos: datetime | None = None
    "Data/hora, por padrão, usa o fim do evento."

    habilitado: bool = True
    "Indica se o formulario esta habilitado para uso."

    perguntasDinamicas: list[PerguntaDinamicaCriar] = Field(default_factory=list)
    "Lista de perguntas dinamicas criadas pelo organizador."


class SubmissaoAvaliacaoCriar(BaseModel):
    """
    Dados enviados pelo usuario ao submeter uma avaliacao.
    """

    respostas: list[RespostaPerguntaAvaliacao]
    "Lista de respostas para as perguntas do formulario."
