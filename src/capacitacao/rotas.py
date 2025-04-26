from pydantic import BaseModel
from src.capacitacao.controlador import CapacitacaoControlador

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    Form,
    HTTPException,
    Request,
    UploadFile,
    status,
)

roteador: APIRouter = APIRouter(
    prefix="/capacitacao",
    tags=["Capacitação"],
)


class PresencaProps(BaseModel):
    codigoPresenca: str
    senha: str


@roteador.post(
    "/registra-presenca",
    name="Registra presença",
    description="Registra a presença de um usuário no sistema.",
    status_code=status.HTTP_201_CREATED,
)
def cadastrarUsuario(
    tasks: BackgroundTasks, request: Request, props: PresencaProps
) -> str:

    if props.senha != "pet1235":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Senha inválida.",
        )

    # despacha para controlador
    presenca = CapacitacaoControlador.registrar_presenca(props.codigoPresenca)

    # retorna os dados do usuario cadastrado
    return presenca
