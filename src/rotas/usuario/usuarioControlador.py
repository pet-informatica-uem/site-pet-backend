import logging
import secrets
from datetime import datetime, timedelta

from fastapi import UploadFile

from src.autenticacao.autenticacao import conferirHashSenha, hashSenha
from src.autenticacao.jwtoken import (
    geraLinkEsqueciSenha,
    geraTokenAtivaConta,
    processaTokenAtivaConta,
    processaTokenTrocaSenha,
)
from src.config import config
from src.email.operacoesEmail import enviarEmailResetSenha, enviarEmailVerificacao
from src.img.operacoesImagem import armazenaFotoUsuario, deletaImagem, validaImagem
from src.modelos.bd import TokenAutenticacaoBD, UsuarioBD, cliente
from src.modelos.excecao import (
    APIExcecaoBase,
    EmailNaoConfirmadoExcecao,
    EmailSenhaIncorretoExcecao,
    ImagemInvalidaExcecao,
    NaoAutenticadoExcecao,
    NaoEncontradoExcecao,
    UsuarioNaoEncontradoExcecao,
)
from src.modelos.usuario.usuario import Petiano, TipoConta, Usuario
from src.modelos.usuario.usuarioClad import (
    UsuarioAtualizar,
    UsuarioAtualizarEmail,
    UsuarioAtualizarSenha,
    UsuarioCriar,
)


class UsuarioControlador:
    @staticmethod
    def ativarConta(token: str) -> None:
        """
        Recebe um token JWT de ativação de conta.

        Caso o token seja válido, ativa a conta.
        """

        # Verifica o token e recupera o email
        msg: dict[str, str] = processaTokenAtivaConta(token)

        # Ativa a conta no BD
        assert msg is not None  # tipagem
        id: str = msg["idUsuario"]
        email: str = msg["email"]

        usuario = UsuarioControlador.getUsuario(id)
        if usuario.email == email:
            usuario.emailConfirmado = True
            UsuarioBD.atualizar(usuario)

    @staticmethod
    def cadastrarUsuario(dadosUsuario: UsuarioCriar) -> str:
        """
        Cria uma conta com os dados fornecidos, e envia um email
        de confirmação de criação de conta ao endereço fornecido.

            A criação da conta pode não suceder por erro na validação de dados,
            por já haver uma conta cadastrada com tal CPF ou email ou por falha
            de conexão com o banco de dados.
        """

        # normaliza dados
        dadosUsuario.email = dadosUsuario.email.lower().strip()
        dadosUsuario.cpf = "".join(c for c in dadosUsuario.cpf if c in "0123456789")
        dadosUsuario.nome = dadosUsuario.nome.strip()
        dadosUsuario.curso = dadosUsuario.curso.strip()

        # hash senha
        dadosUsuario.senha = hashSenha(dadosUsuario.senha.get_secret_value())  # type: ignore

        d = {
            "_id": secrets.token_hex(16),
            "emailConfirmado": False,
            "tipoConta": TipoConta.ESTUDANTE,
            "dataCriacao": datetime.now(),
        }

        d.update(dadosUsuario.model_dump(by_alias=True))
        # cria modelo do usuario
        usuario: Usuario = Usuario(**d)

        # gera token de ativação válido por 24h
        token: str = geraTokenAtivaConta(
            usuario.id, dadosUsuario.email, timedelta(days=1)
        )

        # manda email de ativação
        # não é necessário fazer urlencode pois jwt é url-safe
        linkConfirmacao: str = (
            config.CAMINHO_BASE + "/usuario/confirma-email?token=" + token
        )

        enviarEmailVerificacao(dadosUsuario.email, linkConfirmacao)

        # cria o usuário no bd
        UsuarioBD.criar(usuario)

        return usuario.id

    # Envia um email para trocar de senha se o email estiver cadastrado no bd
    @staticmethod
    def recuperarConta(email: str) -> None:
        UsuarioBD.buscar("email", email)
        # Gera o link e envia o email se o usuário estiver cadastrado
        link: str = geraLinkEsqueciSenha(email)
        enviarEmailResetSenha(email, link)  # Envia o email

    @staticmethod
    def trocarSenha(token: str, senha: str) -> None:
        # Verifica o token e recupera o email
        email: str = processaTokenTrocaSenha(token)

        usuario: Usuario = UsuarioBD.buscar("email", email)

        usuario.senha = hashSenha(senha)

        UsuarioBD.atualizar(usuario)

        logging.info("Senha atualizada para o usuário com ID: " + str(usuario.id))

    @staticmethod
    def autenticarUsuario(email: str, senha: str) -> dict[str, str]:
        """
        Autentica e gera um token de autenticação para o usuário com email e senha
        indicados.
        """

        # verifica senha e usuario
        try:
            usuario: Usuario = UsuarioBD.buscar("email", email)
        except NaoEncontradoExcecao:
            raise EmailSenhaIncorretoExcecao()

        # está ativo?
        if usuario.emailConfirmado != True:
            raise EmailNaoConfirmadoExcecao()

        if not conferirHashSenha(senha, usuario.senha):
            raise EmailSenhaIncorretoExcecao()

        # cria token
        tk: str = secrets.token_urlsafe()
        TokenAutenticacaoBD.criar(
            tk,
            usuario.id,
            datetime.now() + timedelta(days=2),
        )

        # retorna token
        return {"access_token": tk, "token_type": "bearer"}

    @staticmethod
    def getUsuarioAutenticado(token: str) -> Usuario:
        """
        Obtém dados do usuário dono do token fornecido. Falha se o token estiver expirado
        ou for inválido.
        """

        try:
            id: str = TokenAutenticacaoBD.buscar(token).idUsuario
        except NaoEncontradoExcecao:
            raise NaoAutenticadoExcecao()

        if usuario := UsuarioBD.buscar("_id", id):
            return usuario
        else:
            raise NaoAutenticadoExcecao()

    @staticmethod
    def getUsuario(id: str) -> Usuario:
        """
        Obtém dados do usuário com o id fornecido.
        """

        if usuario := UsuarioBD.buscar("_id", id):
            return usuario

        raise UsuarioNaoEncontradoExcecao()

    @staticmethod
    def getUsuarios(petiano: bool = False) -> list[Usuario]:
        return UsuarioBD.listar(petiano)

    @staticmethod
    def editarUsuario(
        id: str,
        dadosUsuario: UsuarioAtualizar,
    ) -> Usuario:
        """
        Atualiza os dados básicos (nome, curso, redes sociais, foto) da conta de um usuário existente.

        Este controlador assume que as redes sociais estejam no formato de links ou None.

        A atualização da conta pode não suceder por erro na validação de dados.
        """

        # obtém usuário
        usuario: Usuario = UsuarioControlador.getUsuario(id)

        # verifica se o usuário é petiano
        if usuario.tipoConta != TipoConta.PETIANO:
            dadosUsuario.github = None
            dadosUsuario.linkedin = None
            dadosUsuario.instagram = None

        # normaliza dados
        if dadosUsuario.nome:
            dadosUsuario.nome = dadosUsuario.nome.strip()
        if dadosUsuario.curso:
            dadosUsuario.curso = dadosUsuario.curso.strip()

        # cria instância de usuario
        d = usuario.model_dump(by_alias=True)
        d.update(dadosUsuario.model_dump(exclude_none=True))
        usuario = Usuario(**d)  # type: ignore

        UsuarioBD.atualizar(usuario)

        return usuario

    @staticmethod
    def deletarUsuario(id: str):
        UsuarioControlador.getUsuario(id)

        UsuarioBD.deletar(id)

    @staticmethod
    def editaSenha(dadosSenha: UsuarioAtualizarSenha, usuario: Usuario) -> None:
        """
        Atualiza a senha de um usuário existente caso a senha antiga seja correta.

        A atualização da conta pode não suceder por erro na validação de dados.
        """
        if conferirHashSenha(dadosSenha.senha.get_secret_value(), usuario.senha):
            usuario.senha = hashSenha(dadosSenha.novaSenha.get_secret_value())
            UsuarioBD.atualizar(usuario)
        else:
            raise APIExcecaoBase(message="Senha incorreta")

    @staticmethod
    def editarEmail(dadosEmail: UsuarioAtualizarEmail, id: str) -> None:
        """
        Atualiza o email de um usuário existente.

        Para UsuarioBD.atualizar o email, o usuário deve digitar sua senha atual.

        O usuário sempre é deslogado quando troca seu email, pois sua conta deve ser reativada.

        A atualização da conta pode não suceder por erro na validação de dados.
        """
        usuario = UsuarioControlador.getUsuario(id)

        if conferirHashSenha(dadosEmail.senha.get_secret_value(), usuario.senha):
            usuario.email = dadosEmail.novoEmail
            usuario.emailConfirmado = False

            UsuarioBD.atualizar(usuario)
            mensagemEmail: str = f"{config.CAMINHO_BASE}/?token={geraTokenAtivaConta(usuario.id, usuario.email, timedelta(hours=24))}"
            enviarEmailVerificacao(usuario.email, mensagemEmail)
        else:
            raise APIExcecaoBase(message="Senha incorreta")

    @staticmethod
    def editarFoto(usuario: Usuario, foto: UploadFile) -> None:
        """
        Atualiza a foto de perfil de um usuário existente.

        Para UsuarioBD.atualizar a foto, o usuário deve inserir uma foto.

        A atualização da conta pode não suceder por erro na validação de dados.
        """
        if not validaImagem(foto.file):
            raise ImagemInvalidaExcecao()

        deletaImagem(usuario.id, ["usuarios"])
        caminhoFotoPerfil: str = armazenaFotoUsuario(usuario.id, foto.file)  # type: ignore
        usuario.foto = caminhoFotoPerfil  # type: ignore

        # atualiza no bd
        UsuarioBD.atualizar(usuario)
