"""
Controlador com regras de negocio para formulários e respostas de avaliacao.
"""

from datetime import datetime
import secrets

from src.modelos.avaliacao.avaliacao import (
    ControleSubmissaoAvaliacao,
    FormularioAvaliacaoEvento,
    PerguntaAvaliacao,
    ResultadoAvaliacaoEvento,
    SecaoAvaliacao,
    SubmissaoAvaliacaoAnonima,
    TipoPerguntaAvaliacao,
)
from src.modelos.avaliacao.avaliacaoClad import (
    ConfiguracaoFormularioCriar,
    SubmissaoAvaliacaoCriar,
)
from src.modelos.bd import AvaliacaoBD, EventoBD
from src.modelos.excecao import APIExcecaoBase, NaoEncontradoExcecao


class AvaliacaoControlador:
    """
    Classe controladora para gerenciar avaliacoes de eventos.
    """

    @staticmethod
    def _montar_perguntas_fixas() -> list[PerguntaAvaliacao]:
        """
        Monta as perguntas fixas obrigatorias do formulario de avaliacao.

        :return perguntas: Lista de perguntas fixas padrao.
        """
        perguntas: list[PerguntaAvaliacao] = []

        def adicionar_pergunta(
            id_pergunta: str,
            texto: str,
            secao: SecaoAvaliacao,
            tipo: TipoPerguntaAvaliacao,
            obrigatoria: bool = True,
            opcoes: list[str] | None = None,
        ):
            perguntas.append(
                PerguntaAvaliacao(
                    idPergunta=id_pergunta,
                    texto=texto,
                    secao=secao,
                    tipo=tipo,
                    obrigatoria=obrigatoria,
                    dinamica=False,
                    opcoes=opcoes,
                    ordem=len(perguntas),
                )
            )

        # Secao Conteudo da atividade.
        adicionar_pergunta(
            id_pergunta="q_cont_relevancia",
            texto="O conteúdo da atividade foi relevante para sua formação/interesse?",
            secao=SecaoAvaliacao.CONTEUDO,
            tipo=TipoPerguntaAvaliacao.ESCALA_UM_A_CINCO,
        )
        adicionar_pergunta(
            id_pergunta="q_cont_profundidade",
            texto="O nível de profundidade do conteúdo foi adequado?",
            secao=SecaoAvaliacao.CONTEUDO,
            tipo=TipoPerguntaAvaliacao.ESCALA_UM_A_CINCO,
        )
        adicionar_pergunta(
            id_pergunta="q_cont_aproveitamento",
            texto="Qual o seu aproveitamento em relação ao que foi ensinado na atividade?",
            secao=SecaoAvaliacao.CONTEUDO,
            tipo=TipoPerguntaAvaliacao.ESCALA_UM_A_CINCO,
        )
        adicionar_pergunta(
            id_pergunta="q_cont_carga_horaria",
            texto="A carga horária foi suficiente para abordar os conteúdos?",
            secao=SecaoAvaliacao.CONTEUDO,
            tipo=TipoPerguntaAvaliacao.MULTIPLA_ESCOLHA,
            opcoes=[
                "Poderia ser menor",
                "Foi suficiente",
                "Poderia ser maior",
                "Não sei opinar",
            ],
        )
        adicionar_pergunta(
            id_pergunta="q_cont_material",
            texto="Gostei do material fornecido.",
            secao=SecaoAvaliacao.CONTEUDO,
            tipo=TipoPerguntaAvaliacao.ESCALA_UM_A_CINCO,
        )
        adicionar_pergunta(
            id_pergunta="q_cont_exercicios_sala",
            texto="Tive facilidade para fazer os exercícios propostos em sala.",
            secao=SecaoAvaliacao.CONTEUDO,
            tipo=TipoPerguntaAvaliacao.ESCALA_UM_A_CINCO,
        )
        adicionar_pergunta(
            id_pergunta="q_cont_exercicios_extras",
            texto="Consegui realizar os exercícios extras e desafios tranquilamente.",
            secao=SecaoAvaliacao.CONTEUDO,
            tipo=TipoPerguntaAvaliacao.ESCALA_UM_A_CINCO,
        )
        adicionar_pergunta(
            id_pergunta="q_cont_ritmo",
            texto="O ritmo da apresentação foi adequado?",
            secao=SecaoAvaliacao.CONTEUDO,
            tipo=TipoPerguntaAvaliacao.ESCALA_UM_A_CINCO,
        )
        adicionar_pergunta(
            id_pergunta="q_cont_comentario",
            texto="Algum comentário sobre o conteúdo da atividade e como ele foi aplicado?",
            secao=SecaoAvaliacao.CONTEUDO,
            tipo=TipoPerguntaAvaliacao.RESPOSTA_LONGA,
            obrigatoria=False,
        )

        # Secao Ministrantes.
        adicionar_pergunta(
            id_pergunta="q_min_conducao",
            texto="Como foi a condução da atividade?",
            secao=SecaoAvaliacao.MINISTRANTES,
            tipo=TipoPerguntaAvaliacao.ESCALA_UM_A_CINCO,
        )
        adicionar_pergunta(
            id_pergunta="q_min_exemplos",
            texto="Os ministrantes deram exemplos suficientes para uma boa absorção dos conteúdos.",
            secao=SecaoAvaliacao.MINISTRANTES,
            tipo=TipoPerguntaAvaliacao.ESCALA_UM_A_CINCO,
        )
        adicionar_pergunta(
            id_pergunta="q_min_dominio",
            texto="Como você avalia o domínio dos ministrantes sobre os conteúdos abordados?",
            secao=SecaoAvaliacao.MINISTRANTES,
            tipo=TipoPerguntaAvaliacao.ESCALA_UM_A_CINCO,
        )
        adicionar_pergunta(
            id_pergunta="q_min_duvidas",
            texto="Os ministrantes conseguiram sanar as dúvidas que surgiram?",
            secao=SecaoAvaliacao.MINISTRANTES,
            tipo=TipoPerguntaAvaliacao.MULTIPLA_ESCOLHA,
            opcoes=["Sim", "Não", "Parcialmente"],
        )
        adicionar_pergunta(
            id_pergunta="q_min_comentario",
            texto="Algum comentário sobre os ministrantes?",
            secao=SecaoAvaliacao.MINISTRANTES,
            tipo=TipoPerguntaAvaliacao.RESPOSTA_LONGA,
            obrigatoria=False,
        )

        # Secao Experiencia geral.
        adicionar_pergunta(
            id_pergunta="q_geral_nota",
            texto="Qual a sua nota para a atividade?",
            secao=SecaoAvaliacao.EXPERIENCIA_GERAL,
            tipo=TipoPerguntaAvaliacao.ESCALA_UM_A_CINCO,
        )
        adicionar_pergunta(
            id_pergunta="q_geral_expectativas",
            texto="A atividade atendeu às suas expectativas?",
            secao=SecaoAvaliacao.EXPERIENCIA_GERAL,
            tipo=TipoPerguntaAvaliacao.MULTIPLA_ESCOLHA,
            opcoes=["Sim", "Não", "Parcialmente"],
        )
        adicionar_pergunta(
            id_pergunta="q_geral_futuras",
            texto="Você teria interesse em participar de futuras atividades do PET-Informática?",
            secao=SecaoAvaliacao.EXPERIENCIA_GERAL,
            tipo=TipoPerguntaAvaliacao.MULTIPLA_ESCOLHA,
            opcoes=["Sim", "Não", "Talvez"],
        )
        adicionar_pergunta(
            id_pergunta="q_geral_temas",
            texto="Quais temas você gostaria que as futuras atividades abordassem?",
            secao=SecaoAvaliacao.EXPERIENCIA_GERAL,
            tipo=TipoPerguntaAvaliacao.RESPOSTA_LONGA,
            obrigatoria=False,
        )
        adicionar_pergunta(
            id_pergunta="q_geral_comentario",
            texto="Alguma sugestão, crítica, elogio ou comentário sobre a atividade?",
            secao=SecaoAvaliacao.EXPERIENCIA_GERAL,
            tipo=TipoPerguntaAvaliacao.RESPOSTA_LONGA,
            obrigatoria=False,
        )

        return perguntas

    @staticmethod
    def configurarFormulario(
        idEvento: str, dadosFormulario: ConfiguracaoFormularioCriar
    ) -> FormularioAvaliacaoEvento:
        """
        Cria ou atualiza o formulario de avaliacao de um evento.

        :param idEvento: Identificador unico do evento.
        :param dadosFormulario: Dados de configuracao do formulario.

        :return formulario: Formulario criado ou atualizado.

        :raises NaoEncontradoExcecao: Lancada caso o evento informado nao exista.
        """
        # Garante que o evento exista antes de configurar o formulario.
        EventoBD.buscar("_id", idEvento)

        perguntas = AvaliacaoControlador._montar_perguntas_fixas()

        for indice, pergunta_dinamica in enumerate(dadosFormulario.perguntasDinamicas, start=len(perguntas)
        ):
            perguntas.append(
                PerguntaAvaliacao(
                    idPergunta=secrets.token_hex(8),
                    texto=pergunta_dinamica.texto.strip(),
                    secao=SecaoAvaliacao.PERSONALIZADA,
                    tipo=pergunta_dinamica.tipo,
                    obrigatoria=pergunta_dinamica.obrigatoria,
                    dinamica=True,
                    opcoes=pergunta_dinamica.opcoes,
                    ordem=indice,
                )
            )

        agora = datetime.now()

        try:
            formulario_existente = AvaliacaoBD.buscarFormularioPorEvento(idEvento)
            dados_formulario = formulario_existente.model_dump(by_alias=True)
            dados_formulario.update(
                perguntas=perguntas,
                liberarApos=dadosFormulario.liberarApos,
                habilitado=dadosFormulario.habilitado,
                dataAtualizacao=agora,
            )
            formulario = FormularioAvaliacaoEvento(**dados_formulario)
            AvaliacaoBD.atualizarFormulario(formulario)
            return formulario
        except NaoEncontradoExcecao:
            formulario = FormularioAvaliacaoEvento(
                _id=secrets.token_hex(16),
                idEvento=idEvento,
                perguntas=perguntas,
                liberarApos=dadosFormulario.liberarApos,
                habilitado=dadosFormulario.habilitado,
                dataCriacao=agora,
                dataAtualizacao=agora,
            )
            AvaliacaoBD.criarFormulario(formulario)
            return formulario

    @staticmethod
    def enviarFormulario(
        idEvento: str, idUsuario: str, submissao: SubmissaoAvaliacaoCriar
    ) -> SubmissaoAvaliacaoAnonima:
        """
        Registra o envio de uma avaliacao por um usuario para um evento.

        :param idEvento: Identificador unico do evento avaliado.
        :param idUsuario: Identificador unico do usuario que esta submetendo.
        :param submissao: Respostas enviadas pelo usuario.

        :return submissaoAnonima: Submissao registrada de forma anonima.

        :raises APIExcecaoBase: Lancada quando o formulario esta desabilitado,
        fora do periodo, com respostas inconsistentes ou com submissao duplicada.
        """
        formulario = AvaliacaoControlador.obterFormulario(idEvento)

        if not formulario.habilitado:
            raise APIExcecaoBase(message="Formulário de avaliação desabilitado.")

        if datetime.now() < formulario.liberarApos:
            raise APIExcecaoBase(message="Formulário de avaliação ainda não liberado.")

        if not EventoBD.verificarInscricaoExistente(idEvento, idUsuario):
          raise APIExcecaoBase(message="Apenas usuários inscritos no evento podem enviar avaliação.")

        if AvaliacaoBD.verificarSubmissaoExistente(idEvento, idUsuario):
            raise APIExcecaoBase(message="Avaliação já realizada para este evento.")

        perguntas_por_id = {pergunta.idPergunta: pergunta for pergunta in formulario.perguntas}
        respostas_por_pergunta: dict[str, bool] = {}

        for resposta in submissao.respostas:
            pergunta = perguntas_por_id.get(resposta.idPergunta)
            if pergunta is None:
                raise APIExcecaoBase(message="Resposta enviada para pergunta inexistente no formulário.")

            if resposta.idPergunta in respostas_por_pergunta:
                raise APIExcecaoBase(message="Cada pergunta deve receber no máximo uma resposta.")
            respostas_por_pergunta[resposta.idPergunta] = True

            if resposta.tipoPergunta != pergunta.tipo:
                raise APIExcecaoBase(message="Tipo de resposta não corresponde a pergunta.")

            if pergunta.tipo == TipoPerguntaAvaliacao.MULTIPLA_ESCOLHA:
                if resposta.respostaOpcao not in (pergunta.opcoes or []):
                    raise APIExcecaoBase(message="Opção selecionada não é válida.")
            elif pergunta.tipo == TipoPerguntaAvaliacao.CAIXAS_DE_SELECAO:
                opcoes_validas = set(pergunta.opcoes or [])
                if not set(resposta.respostasOpcoes or []).issubset(opcoes_validas):
                    raise APIExcecaoBase(message="Uma ou mais opções selecionadas são inválidas.")

        for pergunta in formulario.perguntas:
            if pergunta.obrigatoria and pergunta.idPergunta not in respostas_por_pergunta:
                raise APIExcecaoBase(message="Existem perguntas obrigatórias sem resposta.")

        submissao_anonima = SubmissaoAvaliacaoAnonima(
            _id=secrets.token_hex(16),
            idEvento=idEvento,
            respostas=submissao.respostas,
        )

        controle_submissao = ControleSubmissaoAvaliacao(
            _id=secrets.token_hex(16),
            idEvento=idEvento,
            idUsuario=idUsuario,
            dataSubmissao=datetime.now(),
        )

        AvaliacaoBD.criarSubmissaoAnonima(submissao_anonima)
        AvaliacaoBD.criarControleSubmissao(controle_submissao)

        return submissao_anonima

    @staticmethod
    def obterFormulario(idEvento: str) -> FormularioAvaliacaoEvento:
        """
        Recupera o formulario de avaliacao associado a um evento.

        :param idEvento: Identificador unico do evento.

        :return formulario: Formulario de avaliacao do evento.

        :raises NaoEncontradoExcecao: Lancada se o formulario nao existir.
        """
        return AvaliacaoBD.buscarFormularioPorEvento(idEvento)

    @staticmethod
    def obterRespostaFormulario(
        idEvento: str, idSubmissao: str
    ) -> SubmissaoAvaliacaoAnonima:
        """
        Recupera uma submissao anonima de avaliacao enviada para um evento.

        :param idEvento: Identificador unico do evento.
        :param idSubmissao: Identificador unico da submissao anonima.

        :return submissao: Submissao anonima encontrada para o evento.

        :raises NaoEncontradoExcecao: Lancada quando a submissao nao e encontrada.
        """
        return AvaliacaoBD.buscarSubmissaoAnonima(idEvento, idSubmissao)

    @staticmethod
    def obterResultados(idEvento: str) -> ResultadoAvaliacaoEvento:
        """ 
        Obtem os resultados consolidados de avaliacao de um evento.

        :param idEvento: Identificador unico do evento.

        :return resultado: Estrutura agregada com os resultados do formulario.

        :raises NaoEncontradoExcecao: Lancada quando o formulario do evento nao existe.
        """
        formulario = AvaliacaoControlador.obterFormulario(idEvento)
        submissoes = AvaliacaoBD.listarSubmissoesPorEvento(idEvento)

        perguntas_por_id = {pergunta.idPergunta: pergunta for pergunta in formulario.perguntas}
        soma_notas: dict[str, int] = {}
        quantidade_notas: dict[str, int] = {}
        contagem_opcoes: dict[str, dict[str, int]] = {}
        comentarios: list[str] = []

        for submissao in submissoes:
            for resposta in submissao.respostas:
                pergunta = perguntas_por_id.get(resposta.idPergunta)
                if not pergunta:
                    continue

                if pergunta.tipo == TipoPerguntaAvaliacao.ESCALA_UM_A_CINCO and resposta.nota is not None:
                    soma_notas[pergunta.idPergunta] = soma_notas.get(pergunta.idPergunta, 0) + resposta.nota
                    quantidade_notas[pergunta.idPergunta] = (
                        quantidade_notas.get(pergunta.idPergunta, 0) + 1
                    )
                    continue

                if pergunta.tipo == TipoPerguntaAvaliacao.MULTIPLA_ESCOLHA and resposta.respostaOpcao:
                    contagem = contagem_opcoes.setdefault(pergunta.idPergunta, {})
                    contagem[resposta.respostaOpcao] = contagem.get(resposta.respostaOpcao, 0) + 1
                    continue

                if pergunta.tipo == TipoPerguntaAvaliacao.CAIXAS_DE_SELECAO and resposta.respostasOpcoes:
                    contagem = contagem_opcoes.setdefault(pergunta.idPergunta, {})
                    for opcao in resposta.respostasOpcoes:
                        contagem[opcao] = contagem.get(opcao, 0) + 1
                    continue

                if (pergunta.tipo in (TipoPerguntaAvaliacao.RESPOSTA_CURTA, TipoPerguntaAvaliacao.RESPOSTA_LONGA)
                    and resposta.respostaTexto):
                    comentarios.append(resposta.respostaTexto.strip())

        medias_escala = {
            id_pergunta: round(soma_notas[id_pergunta] / quantidade_notas[id_pergunta], 2)
            for id_pergunta in soma_notas
            if quantidade_notas.get(id_pergunta, 0) > 0
        }

        return ResultadoAvaliacaoEvento(
            idEvento=idEvento,
            totalAvaliacoes=len(submissoes),
            mediasEscala=medias_escala,
            contagemOpcoes=contagem_opcoes,
            comentariosLivres=comentarios,
        )
