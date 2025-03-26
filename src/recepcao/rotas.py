from pydantic import BaseModel
from src.recepcao.controlador import RecepcaoControlador

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
    prefix="/recepcao",
    tags=["Recepção"],
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
    presenca = RecepcaoControlador.registrar_presenca(props.codigoPresenca)

    # retorna os dados do usuario cadastrado
    return presenca
