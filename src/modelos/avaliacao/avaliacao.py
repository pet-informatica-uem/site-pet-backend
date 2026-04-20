"""
Modelos de dados relacionados a avaliacoes de eventos.
"""

from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, model_validator

LIMITE_RESPOSTA_LONGA = 1500
"Quantidade maxima de caracteres para respostas longas."

LIMITE_RESPOSTA_CURTA = 300
"Quantidade maxima de caracteres para respostas curtas."


class TipoPerguntaAvaliacao(str, Enum):
    """
    Tipos de perguntas suportadas pelo modulo de avaliacao.
    """

    RESPOSTA_CURTA = "respostaCurta"
    """Pergunta com resposta textual curta."""

    RESPOSTA_LONGA = "respostaLonga"
    """Pergunta com resposta textual longa."""

    MULTIPLA_ESCOLHA = "multiplaEscolha"
    """Pergunta com opcoes pre-definidas."""

    CAIXAS_DE_SELECAO = "caixasDeSelecao"
    """Pergunta com selecao de uma ou mais opcoes."""

    ESCALA_UM_A_CINCO = "escalaUmACinco"
    """Pergunta com nota inteira na escala de 1 a 5."""


class SecaoAvaliacao(str, Enum):
    """
    Secoes padrao para as perguntas da avaliacao.
    """

    MINISTRANTES = "ministrantes"
    """Perguntas sobre os ministrantes do evento."""

    CONTEUDO = "conteudo"
    """Perguntas sobre conteudo e didatica."""

    EXPERIENCIA_GERAL = "experienciaGeral"
    """Perguntas sobre a experiencia geral no evento."""

    PERSONALIZADA = "personalizada"
    """Perguntas dinamicas criadas pelo organizador."""


class PerguntaAvaliacao(BaseModel):
    """
    Representa uma pergunta do formulario de avaliacao.
    """

    idPergunta: str
    "Identificador unico da pergunta no formulario."

    texto: str
    "Enunciado da pergunta."

    secao: SecaoAvaliacao
    "Secao a qual a pergunta pertence."

    tipo: TipoPerguntaAvaliacao
    "Tipo da pergunta."

    obrigatoria: bool = True
    "Indica se a pergunta deve obrigatoriamente ser respondida."

    dinamica: bool = False
    "Indica se a pergunta foi criada na personalizacao do evento."

    opcoes: list[str] | None = None
    "Lista de opcoes para perguntas de multipla escolha."

    ordem: int = Field(ge=0)
    "Posicao da pergunta no formulario."

    @model_validator(mode="after")
    def validar_regras(self):
        """
        Garante consistencia entre o tipo da pergunta e seus campos.
        """
        if self.tipo is TipoPerguntaAvaliacao.MULTIPLA_ESCOLHA or self.tipo is TipoPerguntaAvaliacao.CAIXAS_DE_SELECAO:
            if not self.opcoes:
                raise ValueError("Perguntas de múltipla escolha e caixas de seleção devem possuir ao menos uma opção.")

            opcoes_validas = [opcao.strip() for opcao in self.opcoes if opcao.strip()]
            if len(opcoes_validas) != len(self.opcoes):
                raise ValueError("Todas as opções devem ser textos não vazios.")

            self.opcoes = opcoes_validas
        elif self.opcoes is not None:
            raise ValueError("A lista de opções deve ser usada apenas em perguntas de multipla escolha.")

        if self.dinamica and self.tipo == TipoPerguntaAvaliacao.ESCALA_UM_A_CINCO:
            raise ValueError("Perguntas dinâmicas devem ser do tipo resposta curta, resposta longa, multipla escolha ou caixas de selecao.")

        return self


class FormularioAvaliacaoEvento(BaseModel):
    """
    Configuracao do formulario de avaliacao de um evento.
    """

    id: str = Field(..., alias="_id")
    "Identificador unico do formulario."

    idEvento: str
    "Identificador do evento associado ao formulario."

    perguntas: list[PerguntaAvaliacao] = Field(default_factory=list)
    "Perguntas fixas e dinamicas que compoem o formulario."

    liberarApos: datetime
    "Data/hora a partir da qual o formulario pode ser respondido."

    habilitado: bool = True
    "Indica se o formulario esta habilitado para uso."

    dataCriacao: datetime
    "Data e hora de criacao do formulario."

    dataAtualizacao: datetime
    "Data e hora da ultima atualizacao do formulario."

    @model_validator(mode="after")
    def validar_secoes_obrigatorias(self):
        """
        Garante a existencia das três seções principais com perguntas obrigatorias.
        """
        secoes_principais = {
            SecaoAvaliacao.MINISTRANTES,
            SecaoAvaliacao.CONTEUDO,
            SecaoAvaliacao.EXPERIENCIA_GERAL,
        }

        secoes_encontradas = {
            pergunta.secao
            for pergunta in self.perguntas
            if not pergunta.dinamica and pergunta.obrigatoria
        }

        if not secoes_principais.issubset(secoes_encontradas):
            raise ValueError("As seções principais de ministrantes, conteúdo e experiência geral devem possuir perguntas obrigatórias.")

        return self

    class Config:
        populate_by_name = True
        json_encoders = {datetime: lambda v: v.isoformat()}


class RespostaPerguntaAvaliacao(BaseModel):
    """
    Representa uma resposta individual para uma pergunta da avaliação.
    """

    idPergunta: str
    "Identificador da pergunta respondida."

    tipoPergunta: TipoPerguntaAvaliacao
    "Tipo de pergunta associado a resposta."

    respostaTexto: str | None = None
    "Resposta textual para perguntas abertas."

    respostaOpcao: str | None = None
    "Opcao escolhida para perguntas de multipla escolha."

    respostasOpcoes: list[str] | None = None
    "Opcoes escolhidas para perguntas com caixas de selecao."

    nota: int | None = Field(default=None, ge=1, le=5)
    "Nota para perguntas na escala de 1 a 5."

    @model_validator(mode="after")
    def validar_resposta(self):
        """
        Garante que o formato da resposta respeita o tipo da pergunta.
        """
        if self.tipoPergunta is TipoPerguntaAvaliacao.RESPOSTA_CURTA or self.tipoPergunta is TipoPerguntaAvaliacao.RESPOSTA_LONGA:
            if not self.respostaTexto or not self.respostaTexto.strip():
                raise ValueError("Perguntas abertas exigem resposta.")

            self.respostaTexto = self.respostaTexto.strip()

            if (self.tipoPergunta is TipoPerguntaAvaliacao.RESPOSTA_CURTA
                and len(self.respostaTexto) > LIMITE_RESPOSTA_CURTA):
                raise ValueError(f"Perguntas de resposta curta aceitam no máximo {LIMITE_RESPOSTA_CURTA} caracteres.")

            if (self.tipoPergunta is TipoPerguntaAvaliacao.RESPOSTA_LONGA
                and len(self.respostaTexto) > LIMITE_RESPOSTA_LONGA):
                raise ValueError(f"Perguntas de resposta longa aceitam no máximo {LIMITE_RESPOSTA_LONGA} caracteres.")

            if (self.respostaOpcao is not None or self.respostasOpcoes is not None or self.nota is not None):
                raise ValueError("Perguntas abertas aceitam apenas o campo respostaTexto.")

        if self.tipoPergunta == TipoPerguntaAvaliacao.MULTIPLA_ESCOLHA:
            if not self.respostaOpcao or not self.respostaOpcao.strip():
                raise ValueError("Perguntas de múltipla escolha exigem uma opção de resposta.")

            if (self.respostaTexto is not None or self.respostasOpcoes is not None or self.nota is not None):
                raise ValueError("Perguntas de múltipla escolha aceitam apenas o campo respostaOpcao.")

        if self.tipoPergunta == TipoPerguntaAvaliacao.CAIXAS_DE_SELECAO:
            if not self.respostasOpcoes:
                raise ValueError("Perguntas com caixas de seleção exigem ao menos uma opção marcada.")

            opcoes_validas = [opcao.strip() for opcao in self.respostasOpcoes if opcao.strip()]
            if len(opcoes_validas) != len(self.respostasOpcoes):
                raise ValueError("As opções selecionadas devem ser textos não vazios.")

            self.respostasOpcoes = opcoes_validas

            if self.respostaTexto is not None or self.respostaOpcao is not None or self.nota is not None:
                raise ValueError("Perguntas com caixas de seleção aceitam apenas o campo respostasOpcoes.")

        if self.tipoPergunta == TipoPerguntaAvaliacao.ESCALA_UM_A_CINCO:
            if self.nota is None:
                raise ValueError("Perguntas de escala exigem nota de 1 a 5.")

            if (self.respostaTexto is not None or self.respostaOpcao is not None or self.respostasOpcoes is not None):
                raise ValueError("Perguntas de escala aceitam apenas o campo nota.")

        return self


class SubmissaoAvaliacaoAnonima(BaseModel):
    """
    Registro anonimo das respostas enviadas para a avaliacao de um evento.
    """

    id: str = Field(..., alias="_id")
    "Identificador unico da submissao anonima."

    idEvento: str
    "Identificador do evento avaliado."

    respostas: list[RespostaPerguntaAvaliacao] = Field(default_factory=list)
    "Respostas enviadas sem qualquer vinculacao com identidade de usuario."

    class Config:
        populate_by_name = True
        json_encoders = {datetime: lambda v: v.isoformat()}


class ControleSubmissaoAvaliacao(BaseModel):
    """
    Controle de voto unico por usuario/evento, separado das respostas anonimas.
    """

    id: str = Field(..., alias="_id")
    "Identificador unico do controle de submissao."

    idEvento: str
    "Identificador do evento avaliado."

    idUsuario: str
    "Identificador do usuario que ja concluiu a avaliacao."

    dataSubmissao: datetime
    "Data e hora em que o usuario concluiu a avaliacao."

    class Config:
        populate_by_name = True
        json_encoders = {datetime: lambda v: v.isoformat()}


class ResultadoAvaliacaoEvento(BaseModel):
    """
    Estrutura de dados para dashboard com resultados consolidados do evento.
    """

    idEvento: str
    "Identificador do evento avaliado."

    totalAvaliacoes: int = 0
    "Quantidade total de avaliacoes recebidas."

    mediasEscala: dict[str, float] = Field(default_factory=dict)
    "Medias calculadas para perguntas de escala."

    contagemOpcoes: dict[str, dict[str, int]] = Field(default_factory=dict)
    "Contagem agregada das opções de múltipla escolha por pergunta."

    comentariosLivres: list[str] = Field(default_factory=list)
    "Lista de comentarios textuais para exibicao no painel de controle."
