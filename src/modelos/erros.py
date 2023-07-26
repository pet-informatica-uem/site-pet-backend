from pydantic import BaseModel, Field


class ErroBase(BaseModel):
    message: str = Field(..., description="A mensagem ou descrição do erro.")
    etc: str = "oi"


class NaoEncontradoErro(ErroBase):
    message: str = Field(..., description="Erro não encontrado.")

class JaExisteErro(ErroBase):
    message: str = Field(..., description="A entidade já existe.")

class AcaoNaoCompletaErro(ErroBase):
    message: str = Field(..., description="Não foi possível concluir a ação.")