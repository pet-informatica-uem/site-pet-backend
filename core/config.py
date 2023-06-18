from pydantic import BaseSettings


class Configuracoes(BaseSettings):
    """
    Classe contendo configurações e constantes globais
    da aplicação.

    Seus atributos podem ser substituídos declarando-se
    uma varíavel de ambiente com prefixo `PET_API_` seguido
    do nome do atributo, ou listando pares de valores e chaves
    em um arquivo `.env` localizado na raiz da aplicação.

    Para acessar os membros dessa classe, basta criar uma instância
    ou acessar a instância global `config` declarada neste módulo.
    """

    EMAIL_SMTP: str = "email-do-email-!"
    """Email SMTP a ser utilizado pela aplicação"""

    SENHA_SMTP: str = "senha-do-email-!"
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

    class Config:
        env_prefix = "PET_API_"

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


config: Configuracoes = Configuracoes()
"""Instância global da classe Configuracoes."""
