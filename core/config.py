from pydantic import BaseSettings


class Configuracoes(BaseSettings):
    EMAIL_SMTP: str = "email-do-email-!"
    SENHA_SMTP: str = "senha-do-email-!"
    SEGREDO_JWT: str = "chave-super-secreta-me-mude-!"
    CAMINHO_BASE: str = "https://www.din.uem.br/pet/api"

    class Config:
        env_prefix = "PET_API_"

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


config: Configuracoes = Configuracoes()
