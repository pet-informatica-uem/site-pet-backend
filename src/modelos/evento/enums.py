from enum import Enum

class TipoVaga(str, Enum):
    """
    Determina se o inscrito utilizará ou não o próprio notebook durante o evento.
    """

    COM_NOTE = "comNotebook"
    """Utilizará o próprio notebook."""

    SEM_NOTE = "semNotebook"
    """Não utilizará o próprio notebook."""

class TipoEvento(str, Enum):
    """
    Determina uma categoria de evento desenvolvido.
    """

    CAPACITACAO = "capacitacao"
    """Curso mais aprofundado, com duração de 4 encontros."""

    WORKSHOP = "workshop"
    """Curso mais abrangente, com duração de 3 encontros."""

    ATIVIDADE_TUTORIAL = "atividade_tutorial"
    """Atividade de aprimoramento, que pode ser interna ou aberta ao público."""

    SECOMP = "secomp"
    """Semana Acadêmica dos cursos do Departamento de Informática."""

    CONECTAPET = "conectapet"
    """Evento acadêmico em parceria com o grupo Conectadas."""

    OUTRO = "outro"
    """Outra categoria de evento."""

class NivelConhecimento(str, Enum):
    """
    Determina o nível de conhecimento de um inscrito a respeito do tema do evento, em uma escala de 1 a 5.
    """

    NENHUM = "1"
    """Não possui conhecimento prévio."""

    BASICO = "2"
    """Possui conhecimento básico."""

    INTERMEDIARIO = "3"
    """Possui conhecimento intermediário."""

    AVANCADO = "4"
    """Possui conhecimento avançado."""

    ESPECIALISTA = "5"
    """Domina o assunto."""