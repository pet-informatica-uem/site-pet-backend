from pydantic import BaseModel, Field


class ErroBase(BaseModel):
    message: str = Field(..., description="A mensagem ou descrição do erro.")
    etc: str = "oi"


class NaoAutenticadoErro(ErroBase):
    pass


class NaoEncontradoErro(ErroBase):
    pass


class JaExisteErro(ErroBase):
    pass
