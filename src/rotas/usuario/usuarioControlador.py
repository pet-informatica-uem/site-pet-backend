import logging
import secrets
from datetime import datetime, timedelta
from fastapi import UploadFile
from autenticacao.autenticacao import conferirHashSenha, hashSenha

from autenticacao.jwtoken import geraLink, geraTokenAtivaConta, processaTokenAtivaConta, processaTokenTrocaSenha
from email.operacoesEmail import resetarSenha, verificarEmail
from img.operacoesImagem import deletaImagem
from modelos.autenticacao.autenticacaoTokenBD import AuthTokenBD
from modelos.usuario.usuario import EstadoConta, TipoConta, UsuarioSenha
from modelos.usuario.usuarioBD import UsuarioBD
from rotas.usuario.usuarioUtil import ativaconta, atualizaSenha, verificaSeUsuarioExiste
from src.config import config


def ativaContaControlador(token: str) -> dict:
    """
    Recebe um token JWT de ativação de conta.

    Caso o token seja válido, ativa a conta e retorna um dicionário
    com campo "status" igual a "200".

    Caso contrário, retorna um dicionário com campo "status" diferente
    de "200" e um campo "mensagem" contendo uma mensagem de erro.
    """

    # Verifica o token e recupera o email
    retorno = processaTokenAtivaConta(token)
    if retorno.get("status") != "200":
        return retorno

    # Ativa a conta no BD
    msg = retorno.get("mensagem")
    assert msg is not None  # tipagem
    id = msg["idUsuario"]
    email = msg["email"]

    retorno = ativaconta(id, email)

    return retorno


def cadastraUsuarioControlador(
    *, nomeCompleto: str, cpf: str, email: str, senha: str, curso: str | None
) -> dict:
    """
    Cria uma conta com os dados fornecidos, e envia um email
    de confirmação de criação de conta ao endereço fornecido.

    Este controlador assume que o cpf e email já estão nas formas
    normalizadas (cpf contendo 11 dígitos, email sem espaço em branco
    prefixado ou sufixado e com todos os caracteres em caixa baixa).

    Retorna um dicionário contendo campos "status" e "mensagem".

    - Se a conta foi criada com sucesso, "status" == "201" e "mensagem" conterá
    o _id da conta (str).
    - Se a conta não foi criada com sucesso, "status" != "201" e "mensagem" conterá
    uma mensagem de erro (str).

    A criação da conta pode não suceder por erro na validação de dados,
    por já haver uma conta cadastrada com tal CPF ou email ou por falha
    de conexão com o banco de dados.
    """

    # 3. verifico se o email já existe e crio o usuário
    try:
        bd = UsuarioBD()
        resultado = bd.criarUsuario(
            {
                "nome": nomeCompleto,
                "email": email,
                "cpf": cpf,
                "curso": curso,
                "estado da conta": EstadoConta.INATIVO,
                "senha": hashSenha(senha),
                "tipo conta": TipoConta.ESTUDANTE,
                "data criacao": datetime.now(),
            }
        )

        if resultado["status"] != "200":
            return resultado

        id = str(resultado["mensagem"])

        # 4. gera token de ativação válido por 24h
        token = geraTokenAtivaConta(id, email, timedelta(days=1))

        # 5. manda email de ativação
        # não é necessário fazer urlencode pois jwt é url-safe
        linkConfirmacao = (
            config.CAMINHO_BASE + "/usuario/confirmacaoEmail?token=" + token
        )
        # print(linkConfirmacao)
        resultado = verificarEmail(
            config.EMAIL_SMTP, config.SENHA_SMTP, email, linkConfirmacao
        )

        if resultado["status"] != "200":
            # return {"status": "400", "mensagem": "Erro no envio do email."}
            # não indicar que o email não existe para evitar spam
            pass

        return {"status": "201", "mensagem": id}
    except Exception as e:
        logging.error("Erro no cadastro de usuário: " + str(e))
        return {"status": "500", "mensagem": str(e)}


# Envia um email para trocar de senha se o email estiver cadastrado no bd
def recuperaContaControlador(email: str) -> dict:
    # Verifica se o usuário está cadastrado no bd
    retorno = verificaSeUsuarioExiste(email)
    if retorno.get("status") == "500":
        return retorno

    # Gera o link e envia o email se o usuário estiver cadastrado
    if retorno.get("status") == "200":
        link = geraLink(email)
        resetarSenha(config.EMAIL_SMTP, config.SENHA_SMTP, email, link)  # Envia o email

    return {"mensagem": "OK", "status": "200"}


def trocaSenhaControlador(token, senha: str) -> dict:
    # Verifica o token e recupera o email
    retorno = processaTokenTrocaSenha(token)
    if retorno.get("status") != "200":
        return retorno

    # Atualiza a senha no bd
    email = retorno.get("email")
    retorno = atualizaSenha(email, senha)

    return retorno


def autenticaUsuarioControlador(email: str, senha: str) -> dict:
    """
    Autentica e gera um token de autenticação para o usuário com email e senha
    indicados.

    Retorna um dicionário com campos "status" e "mensagem".

    - "status" == "200" se e somente se a autenticação ocorreu com sucesso.
    - "mensagem" contém um token de autenticação no formato OAuth2 se autenticado com
      sucesso, ou uma mensagem de erro caso contrário.
    """
    try:
        # verifica senha
        conexaoUsuario = UsuarioBD()

        resp = conexaoUsuario.getIdUsuario(email)
        if resp["status"] != "200":
            return resp
        id = resp["mensagem"]

        resp = conexaoUsuario.getUsuario(id)
        if resp["status"] != "200":
            return resp
        usuario = UsuarioSenha.deBd(resp["mensagem"])

        if not conferirHashSenha(senha, usuario.senha):
            return {"status": "401", "mensagem": "Não autenticado"}

        # está ativo?
        if usuario.estadoConta != EstadoConta.ATIVO:
            return {"status": "403", "mensagem": "Não autorizado"}

        # cria token
        tk = secrets.token_urlsafe()
        conexaoToken = AuthTokenBD()
        resp = conexaoToken.criarToken(
            {
                "_id": tk,
                "idUsuario": usuario.id,
                "validade": datetime.now() + timedelta(days=2),
            }
        )
        if resp["status"] != "200":
            return resp

        # retorna token
        return {
            "status": "200",
            "mensagem": {"access_token": tk, "token_type": "bearer"},
        }
    except Exception as e:
        logging.error("Erro no cadastro de usuário: " + str(e))
        return {"status": "500", "mensagem": str(e)}


def getUsuarioAutenticadoControlador(token: str) -> dict:
    """
    Obtém dados do usuário dono do token fornecido. Falha se o token estiver expirado
    ou for inválido.

    Retorna um dicionário com campos "status" e "mensagem".
    - "status" == "200" se e somente se os dados foram recuperados com sucesso.
    - "mensagem" contém uma instância da classe UsuarioSenha em caso de sucesso e uma
      mensagem de erro caso contrário.
    """
    try:
        conexaoAuthToken = AuthTokenBD()

        resp = conexaoAuthToken.getIdUsuarioDoToken(token)
        if resp["status"] != "200":
            return resp
        id = resp["mensagem"]

        conexaoUsuario = UsuarioBD()

        resp = conexaoUsuario.getUsuario(id)
        if resp["status"] != "200":
            return resp

        usuario = UsuarioSenha.deBd(resp["mensagem"])
        return {"status": "200", "mensagem": usuario}
    except Exception as e:
        logging.error("Erro na autenticação: " + str(e))
        return {"status": "500", "mensagem": str(e)}


def getUsuarioControlador(id: str) -> dict:
    """
    Obtém dados do usuário com o id fornecido.

    Retorna um dicionário com campos "status" e "mensagem".

    - "status" == "200" se e somente se os dados foram recuperados com sucesso.
    - "mensagem" contém uma instância da classe UsuarioSenha em caso de sucesso e uma
      mensagem de erro caso contrário.
    """
    try:
        conexaoUsuario = UsuarioBD()

        resp = conexaoUsuario.getUsuario(id)
        if resp["status"] != "200":
            return resp

        usuario = UsuarioSenha.deBd(resp["mensagem"])
        return {"status": "200", "mensagem": usuario}
    except Exception as e:
        logging.error("Erro ao recuperar dados do usuário: " + str(e))
        return {"status": "500", "mensagem": str(e)}


def editaUsuarioControlador(
    *, usuario: UsuarioSenha, nomeCompleto: str, curso: str | None, redesSociais: dict
) -> dict:
    """
    Atualiza os dados básicos (nome, curso, redes sociais) da conta de um usuário existente.

    Este controlador assume que as redes sociais estejam no formato de links ou None.

    Retorna um dicionário contendo campos "status" e "mensagem".

    - Se a conta foi atualizada, "status" == "200" e "mensagem" conterá
    o _id da conta (str).
    - Se a conta não foi atualizada com sucesso, "status" != "200" e "mensagem" conterá
    uma mensagem de erro (str).

    A atualização da conta pode não suceder por erro na validação de dados.
    """
    try:
        bd = UsuarioBD()
        usuarioDados: dict = usuario.paraBd()

        usuarioDados.update(
            {
                "nome": nomeCompleto,
                "curso": curso,
                "redes sociais": redesSociais,
            }
        )
        id = usuarioDados.pop("_id")
        atualizacao = bd.atualizarUsuario(id, usuarioDados)
        if atualizacao["status"] == "200":
            logging.info("Dados do usuário atualizados, id: " + str(id))
            return {"status": "200", "mensagem": "Usuário atualizado com sucesso."}
        else:
            logging.error(
                "Erro no banco de dados ao fazer a atualização: "
                + str(atualizacao["mensagem"])
            )
            return {
                "status": atualizacao["status"],
                "mensagem": atualizacao["mensagem"],
            }
    except Exception as e:
        logging.error("Erro na atualização de usuário: " + str(e))
        return {"status": "500", "mensagem": str(e)}


def editaSenhaControlador(*, senhaAtual: str, novaSenha: str, usuario: UsuarioSenha) -> dict:
    """
    Atualiza a senha de um usuário existente.

    Para atualizar a senha, o usuário deve digitar sua senha atual.

    Retorna um dicionário contendo campos "status" e "mensagem".

    - Se a senha foi atualizada, "status" == "200" e "mensagem" conterá
    o _id da conta (str).
    - Se a senha não foi atualizada com sucesso, "status" != "200" e "mensagem" conterá
    uma mensagem de erro (str).

    A atualização da conta pode não suceder por erro na validação de dados.
    """
    try:
        bd = UsuarioBD()
        usuarioDados: dict = usuario.paraBd()
        if conferirHashSenha(senhaAtual, usuarioDados["senha"]):
            usuarioDados.update({"senha": hashSenha(novaSenha)})
            id = usuarioDados.pop("_id")
            atualizacao = bd.atualizarUsuario(id, usuarioDados)
            if atualizacao["status"] == "200":
                logging.info("Dados do usuário atualizados, id: " + str(id))
                return {
                    "status": "200",
                    "mensagem": "Usuário atualizado com sucesso.",
                }
            else:
                logging.error(
                    "Erro no banco de dados ao fazer a atualização: "
                    + str(atualizacao["mensagem"])
                )
                return {
                    "status": atualizacao["status"],
                    "mensagem": atualizacao["mensagem"],
                }
        else:
            return {"status": "400", "mensagem": "Senha incorreta"}
    except Exception as e:
        logging.error("Erro na atualização de senha do Usuário: " + str(e))
        return {"status": "500", "mensagem": str(e)}


def editaEmailControlador(*, senhaAtual: str, novoEmail: str, usuario: UsuarioSenha) -> dict:
    """
    Atualiza o email de um usuário existente.

    Para atualizar o email, o usuário deve digitar sua senha atual.

    O usuário sempre é deslogado quando troca seu email, pois sua conta deve ser reativada.

    Retorna um dicionário contendo campos "status" e "mensagem".

    - Se o email foi atualizado, "status" == "200" e "mensagem" conterá
    o _id da conta (str).
    - Se o email não foi atualizado com sucesso, "status" != "200" e "mensagem" conterá
    uma mensagem de erro (str).

    A atualização da conta pode não suceder por erro na validação de dados.
    """
    try:
        bd = UsuarioBD()
        usuarioDados: dict = usuario.paraBd()
        if conferirHashSenha(senhaAtual, usuarioDados["senha"]):
            usuarioDados.update({"email": novoEmail, "estado da conta": "inativo"})
            id = usuarioDados.pop("_id")
            atualizacao = bd.atualizarUsuario(id, usuarioDados)
            if atualizacao["status"] == "200":
                token24h = geraTokenAtivaConta(id, novoEmail, timedelta(days=1))
                linkConfirmacao = (
                    config.CAMINHO_BASE
                    + "/usuario/confirmacaoEmail?token="
                    + token24h
                )
                verificarEmail(
                    emailPet=config.EMAIL_SMTP,
                    senhaPet=config.SENHA_SMTP,
                    emailDestino=novoEmail,
                    link=linkConfirmacao,
                )
                logging.info("Dados do usuário atualizados, id: " + str(id))
                return {
                    "status": "200",
                    "mensagem": "Usuário atualizado com sucesso.",
                }
            else:
                logging.error(
                    "Erro no banco de dados ao fazer a atualização: "
                    + str(atualizacao["mensagem"])
                )
                return {
                    "status": atualizacao["status"],
                    "mensagem": atualizacao["mensagem"],
                }
        else:
            return {"status": "400", "mensagem": "Senha incorreta"}
    except Exception as e:
        logging.error("Erro na atualização de email do Usuário: " + str(e))
        return {"status": "500", "mensagem": str(e)}
      

def editarFotoControlador(*, usuario: UsuarioSenha, foto: dict[str, UploadFile]) -> dict:
    """
    Atualiza a foto de perfil de um usuário existente.

    Para atualizar a foto, o usuário deve inserir uma foto.

    Retorna um dicionário contendo campos "status" e "mensagem".

    - Se a foto for atualizada, "status" == "200" e "mensagem" conterá
    o _id da conta (str).
    - Se a foto não for atualizado com sucesso, "status" != "200" e "mensagem" conterá
    uma mensagem de erro (str).

    A atualização da conta pode não suceder por erro na validação de dados.
    """
    try:
        bd = UsuarioBD()
        usuarioDados: dict = usuario.paraBd()

        if not validaImagem(foto["mensagem"].file):  # type: ignore
            return {"mensagem": "Foto de perfil inválida.", "status": "400"}

        deletaImagem(usuarioDados["nome"], "usuarios")
        caminhoFotoPerfil = armazenaFotoUsuario(usuarioDados["nome"], foto["mensagem"].file)  # type: ignore
        usuarioDados["foto perfil"] = caminhoFotoPerfil
        id = usuarioDados.pop("_id")
        atualizacao = bd.atualizarUsuario(id, usuarioDados)
        if atualizacao["status"] == "200":
            logging.info("Dados do usuário atualizados, id: " + str(id))
            return {
                "status": "200",
                "mensagem": "Usuário atualizado com sucesso.",
            }
        else:
            logging.error(
                "Erro no banco de dados ao fazer a atualização: "
                + str(atualizacao["mensagem"])
            )
            return {
                "status": atualizacao["status"],
                "mensagem": atualizacao["mensagem"],
            }
    except Exception as e:
        logging.error("Erro na atualização de foto de perfil do Usuário: " + str(e))
        return {"status": "500", "mensagem": str(e)}