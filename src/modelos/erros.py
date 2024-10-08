from pydantic import BaseModel, Field


class ErroBase(BaseModel):
    message: str = Field(..., description="A mensagem ou descrição do erro.")


class NaoEncontradoErro(ErroBase):
    message: str = Field(..., description="Erro não encontrado.")


class JaExisteErro(ErroBase):
    message: str = Field(..., description="A entidade já existe.")


class AcaoNaoCompletaErro(ErroBase):
    message: str = Field(..., description="Não foi possível concluir a ação.")


class NaoAutenticadoErro(ErroBase):
    message: str = Field(..., description="Usuário não autenticado.")


class NaoAutorizadoErro(ErroBase):
    message: str = Field(..., description="Acesso negado.")
