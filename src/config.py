from datetime import datetime, timedelta
from pathlib import Path

from pydantic_core import Url
from pydantic_settings import BaseSettings, SettingsConfigDict


# Horario inicio para as rotinas
def horarioInicio() -> datetime:
    """
    Retorna o próximo horário de início das rotinas.
    """

    hoje = datetime.now()
    amanha = hoje + timedelta(days=1)
    amanhaMeiaNoite = datetime.combine(
        amanha, datetime.min.time()
    )  # Meia noite de amanhã
    amanha3daManha = amanhaMeiaNoite + timedelta(hours=3)  # 3 da manhã de amanhã

    return amanha3daManha


class Configuracoes(BaseSettings):
    """
    Classe contendo configurações e constantes globais
    da aplicação.

    Seus atributos podem ser substituídos declarando-se
    uma varíavel de ambiente com prefixo `PET_API_` seguido
    do nome do atributo, ou listando pares de valores e chaves
    em um arquivo `.env` localizado na raiz da aplicação
    (ex PET_API_EMAIL_SMTP=email@pet.com).

    Para acessar os membros dessa classe, basta criar uma instância
    ou acessar a instância global `config` declarada neste módulo.
    """

    EMAIL_SMTP: str = "EMAIL-NAO-MUDAR-AQUI-VEJA-O-COMENTÁRIO-ACIMA-!"
    """Email SMTP a ser utilizado pela aplicação"""

    SENHA_SMTP: str = "SENHA-NÃO-MUDAR-AQUI-VEJA-O-COMENTÁRIO-ACIMA-!"
    """Senha SMTP a ser utilizada pela aplicação"""

    SEGREDO_JWT: str = "chave-super-secreta-me-mude-!"
    """
    Segredo utilizado na geração de tokens de autenticação.
    Deve ser alterado antes da aplicação ser posta no ar.
    """

    CAMINHO_BASE: str = "https://www.din.uem.br/pet/api"
    """
    URL base da aplicação na web. Utilizado na geração de links
    para serem exibidos e enviados aos usuários.
    """

    CAMINHO_IMAGEM: Path = Path.cwd() / "img"
    """
    Caminho onde serão armazenadas as imagens (.../img/). 
    """

    URI_BD: Url = Url("mongodb://localhost:27017/")
    """
    URI para o banco de dados MongoDB.
    """

    NOME_BD: str = "petBD"
    """
    Nome do banco de dados utilizado pela aplicação.
    """

    HORARIO_INICIO_ROTINAS: datetime = horarioInicio()
    """
    Horário de início das rotinas.
    """

    MOCK_EMAIL: bool = False
    """
    Caso verdadeiro, não envia emails mas imprime o conteúdo deles na saída padrão.
    """

    MOCK_BD: bool = False
    """
    Caso verdadeiro, usa um banco de dados de teste.
    """

    ROOT_PATH: str = ""
    """
    URL-raiz do servidor.
    """

    SERVIDOR_SMTP: str = "smtp.gmail.com"
    """
    Servidor SMTP a ser utilizado.
    """

    PORTA_SMTP: int = 587
    """
    Porta do servidor SMTP a ser utilizada.
    """

    SMTP_TLS: bool = True
    """
    Caso verdadeiro, utiliza TLS na conexão com o servidor SMTP.
    """

    model_config = SettingsConfigDict(
        env_prefix="PET_API_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


config: Configuracoes = Configuracoes()
"""Instância global da classe Configuracoes."""
