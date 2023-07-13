import logging
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    Form,
    HTTPException,
    Request,
    Response,
    status,
    UploadFile,
)
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, HttpUrl, SecretStr
from modelos.autenticacao.autenticacaoTokenBD import AuthTokenBD
from modelos.usuario.usuario import Usuario, UsuarioSenha

from modelos.usuario.validacaoCadastro import validaCpf, validaEmail, validaSenha
from rotas.usuario.usuarioControlador import ativaContaControlador, autenticaUsuarioControlador, cadastraUsuarioControlador, editaEmailControlador, editaSenhaControlador, editaUsuarioControlador, editarFotoControlador, getUsuarioAutenticadoControlador, getUsuarioControlador, recuperaContaControlador, trocaSenhaControlador


roteador = APIRouter(
    prefix="/usuario",
    tags=["Usuário"],
)


@roteador.post(
    "/cadastrar",
    name="Cadastrar usuário",
    description="Cadastra um novo usuário com os dados fornecidos.\n"
    "Os dados fornecidos devem ser válidos. Os requisitos de senha são:\n"
    " - Deve possuir entre 8 e 64 caracteres\n"
    " - Deve ter ao menos uma letra maiúscula\n"
    " - Deve ter ao menos um dígito\n"
    " - Deve ter ao menos um caractere não alfanumérico\n",
    status_code=status.HTTP_201_CREATED,
)
def cadastrarUsuario(
    nomeCompleto: Annotated[str, Form(max_length=200)],
    cpf: Annotated[str, Form(max_length=200)],
    email: Annotated[EmailStr, Form()],
    senha: Annotated[SecretStr, Form(max_length=200)],
    confirmacaoSenha: Annotated[SecretStr, Form(max_length=200)],
    curso: Annotated[str | None, Form(max_length=200)] = None,
):
    # valida dados
    if (
        not validaCpf(cpf)
        or not validaSenha(
            senha.get_secret_value(), confirmacaoSenha.get_secret_value()
        )
        or not validaEmail(email)
    ):
        logging.info(
            "Tentativa de cadastro de usuário com cpf, senha ou email inválido."
            + f" (CPF={cpf} Email={email})"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Dados inválidos"
        )

    # normaliza dados
    email = EmailStr(email.lower().strip())
    cpf = "".join(c for c in cpf if c in "0123456789")

    # despacha para controlador
    resultado = cadastraUsuarioControlador(
        nomeCompleto=nomeCompleto,
        cpf=cpf,
        email=email,
        senha=senha.get_secret_value(),
        curso=curso,
    )
    if resultado["status"] != "201":
        logging.info(
            "Tentativa de cadastro de usuário falhou. Dados: "
            + str(resultado["mensagem"])
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Dados inválidos"
        )

    # retorna OK
    return resultado["mensagem"]


@roteador.get(
    "/confirmacaoEmail",
    name="Confirmação de email",
    description="Confirma o email de uma conta através do token suprido.",
    status_code=status.HTTP_200_OK,
)
def confirmaEmail(token: str):
    resultado = ativaContaControlador(token)
    if resultado["status"] != "200":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Token inválido."
        )


@roteador.post(
    "/recupera",
    name="Recuperar conta",
    description="""
        Envia um email para a conta fornecida para trocar a senha.
        Falha, caso o email da conta seja inválido ou não esteja relacionado a uma conta cadastrada.
    """,
)
def recuperaConta(
    email: Annotated[EmailStr, Form()], request: Request, response: Response
):
    email = EmailStr(email.lower())

    # Verifica se o email é válido
    if not validaEmail(email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email inválido.",
        )

    # Passa o email para o controlador
    resposta = recuperaContaControlador(email)

    response.status_code = int(resposta["status"])
    return {"mensagem": resposta.get("mensagem")}


@roteador.post(
    "/troca-senha",
    name="Trocar senha",
    description="""
        Altera a senha do usuário. Falha, se a senha ou o link forem inválidos.
    """,
    status_code=status.HTTP_200_OK,
)
def trocaSenha(token, senha: Annotated[str, Form()], response: Response):
    # Validacao basica da senha
    if not validaSenha(senha, senha):
        raise HTTPException(status_code=400, detail="Senha inválida.")

    # Despacha o token para o controlador
    retorno = trocaSenhaControlador(token, senha)

    response.status_code = int(retorno.get("status"))
    return {"mensagem": retorno.get("mensagem")}


class Token(BaseModel):
    access_token: str
    token_type: str


@roteador.post(
    "/token",
    name="Autenticar",
    description="""
    Autentica o usuário através do email e senha fornecidos.
    """,
    status_code=status.HTTP_200_OK,
    response_model=Token,
)
def autenticar(dados: Annotated[OAuth2PasswordRequestForm, Depends()]):
    exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não autenticado",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # obtém dados
    email = dados.username
    senha = dados.password

    # normaliza email
    email = email.lower().strip()

    # chama controlador
    resp = autenticaUsuarioControlador(email, senha)
    if resp["status"] != "200":
        raise exc

    return resp["mensagem"]


tokenAcesso = OAuth2PasswordBearer(tokenUrl="/usuario/token")


def getUsuarioAutenticado(token: Annotated[str, Depends(tokenAcesso)]):
    resp = getUsuarioAutenticadoControlador(token)
    if resp["status"] != "200":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não autenticado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    else:
        return resp["mensagem"]


def getPetianoAutenticado(
    usuario: Annotated[UsuarioSenha, Depends(getUsuarioAutenticado)]
):
    if usuario.tipoConta == "petiano":
        return usuario
    raise HTTPException(status_code=401, detail="Acesso negado.")


@roteador.get(
    "/id/eu",
    name="Obter detalhes do usuário autenticado",
    description="""
    Retorna detalhes do usuário autenticado.
    """,
    status_code=status.HTTP_200_OK,
    response_model=Usuario,
)
def getUsuarioEu(usuario: Annotated[UsuarioSenha, Depends(getUsuarioAutenticado)]):
    return usuario


@roteador.get(
    "/id/{id}",
    name="Obter detalhes do usuário autenticado",
    description="""
    Retorna detalhes do usuário autenticado.
    """,
    status_code=status.HTTP_200_OK,
    response_model=Usuario,
)
def getUsuario(_token: Annotated[str, Depends(tokenAcesso)], id: str):
    resp = getUsuarioControlador(id)
    if resp["status"] != "200":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado",
        )
    else:
        return resp["mensagem"]


@roteador.post(
    "/id/eu/editar-foto",
    name="Atualizar foto de perfil",
    description="O usuário petiano é capaz de editar sua foto de perfil",
)
def editarFoto(
    foto: UploadFile | None,
    usuario: Annotated[UsuarioSenha, Depends(getUsuarioAutenticado)] = ...,
) -> dict:
    resultado = {"status": "200", "mensagem": foto}

    editarFotoControlador(usuario=usuario, foto=resultado)
    
    return resultado
  
  
@roteador.post(
    "/id/eu/editar-dados",
    name="Editar dados do usuário autenticado",
    description="""O usuário é capaz de editar os dados""",
)
def editarDados(
    nomeCompleto: Annotated[str, Form(max_length=200)],
    curso: Annotated[str, Form(max_length=200)],
    github: Annotated[HttpUrl, Form()],
    instagram: Annotated[HttpUrl, Form()],
    linkedin: Annotated[HttpUrl, Form()],
    twitter: Annotated[HttpUrl, Form()],
    usuario: Annotated[UsuarioSenha, Depends(getUsuarioAutenticado)] = ...,
):
    
    # agrupa redes sociais
    redesSociais = {
        "github": github,
        "linkedin": linkedin,
        "instagram": instagram,
        "twitter": twitter,
    }

    # valida links
    for chave in redesSociais:
        link = str(redesSociais[chave])
        if chave not in link:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="O link "
                + link
                + " não é válido com a rede social "
                + chave,
            )

    resultado = editaUsuarioControlador(
        usuario=usuario,
        nomeCompleto=nomeCompleto,
        curso=curso,
        redesSociais=redesSociais,
    )

    return resultado


@roteador.post(
    "/id/eu/alterar-senha",
    name="Editar senha do usuário autenticado",
    description="""O usuário é capaz de editar sua senha\n
    Caso a opção deslogarAoTrocarSenha for ativada, todos as sessões serão deslogadas ao trocar a senha.""",
)
def editarSenha(
    senhaAtual: Annotated[SecretStr, Form(max_length=200)],
    novaSenha: Annotated[SecretStr, Form(max_length=200)],
    confirmacaoSenha: Annotated[SecretStr, Form(max_length=200)],
    deslogarAoTrocarSenha: Annotated[bool, Form()],
    usuario: Annotated[UsuarioSenha, Depends(getUsuarioAutenticado)] = ...,
    token: Annotated[str, Depends(tokenAcesso)] = ...,
):
    
    # verifica nova senha
    if not validaSenha(
        novaSenha.get_secret_value(), confirmacaoSenha.get_secret_value()
    ):
        logging.info("Erro. Nova senha não foi validada com sucesso.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Dados inválidos"
        )

    # efetua troca de senha
    resultado = editaSenhaControlador(
        senhaAtual=senhaAtual.get_secret_value(),
        novaSenha=novaSenha.get_secret_value(),
        usuario=usuario,
    )

    # efetua logout de todas as sessões, caso o usuário desejar
    if deslogarAoTrocarSenha and resultado["status"] == "200":
        gerenciarTokens = AuthTokenBD()
        gerenciarTokens.deletarTokensUsuario(
            gerenciarTokens.getIdUsuarioDoToken(token=token)["mensagem"]
        )

    return resultado


@roteador.post(
    "/id/eu/alterar-email",
    name="Editar email do usuário autenticado",
    description="""O usuário é capaz de editar seu email""",
)
def editarEmail(
    senhaAtual: Annotated[SecretStr, Form(max_length=200)],
    novoEmail: Annotated[EmailStr, Form()],
    usuario: Annotated[UsuarioSenha, Depends(getUsuarioAutenticado)] = ...,
    token: Annotated[str, Depends(tokenAcesso)] = ...,
):
    
    if not validaEmail(novoEmail):
        logging.info("Erro. Novo email não foi validado com sucesso.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Dados inválidos"
        )

    # normaliza dados
    novoEmail = EmailStr(novoEmail.lower().strip())

    resultado = editaEmailControlador(
        senhaAtual=senhaAtual.get_secret_value(),
        novoEmail=novoEmail,
        usuario=usuario,
    )

    if resultado["status"] == "200":
        gerenciarTokens = AuthTokenBD()
        gerenciarTokens.deletarTokensUsuario(
            gerenciarTokens.getIdUsuarioDoToken(token=token)["mensagem"]
        )
    
    return resultado