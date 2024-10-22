import logging
import secrets
from datetime import datetime, timedelta

from fastapi import BackgroundTasks, UploadFile

from src.autenticacao.autenticacao import conferirHashSenha, hashSenha
from src.autenticacao.jwtoken import (
    geraLinkEsqueciSenha,
    geraTokenAtivaConta,
    processaTokenAtivaConta,
    processaTokenTrocaSenha,
)
from src.config import config
from src.email.operacoesEmail import (
    DadoAlterado,
    enviarEmailAlteracaoDados,
    enviarEmailResetSenha,
    enviarEmailVerificacao,
)
from src.img.operacoesImagem import armazenaFotoUsuario, deletaImagem, validaImagem
from src.modelos.bd import RegistroLoginBD, TokenAutenticacaoBD, UsuarioBD, cliente
from src.modelos.excecao import (
    APIExcecaoBase,
    EmailNaoConfirmadoExcecao,
    EmailSenhaIncorretoExcecao,
    ImagemInvalidaExcecao,
    ImagemNaoSalvaExcecao,
    NaoAtualizadaExcecao,
    NaoAutenticadoExcecao,
    NaoEncontradoExcecao,
    UsuarioNaoEncontradoExcecao,
)
from src.modelos.registro.registroLogin import RegistroLogin
from src.modelos.usuario.usuario import Petiano, TipoConta, Usuario
from src.modelos.usuario.usuarioClad import (
    UsuarioAtualizar,
    UsuarioAtualizarEmail,
    UsuarioAtualizarSenha,
    UsuarioCriar,
)
from src.modelos.usuario.validacaoCadastro import ValidacaoCadastro


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
    def cadastrarUsuario(dadosUsuario: UsuarioCriar, tasks: BackgroundTasks) -> str:
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
            config.CAMINHO_BASE + "/usuarios/confirma-email?token=" + token
        )

        tasks.add_task(enviarEmailVerificacao, dadosUsuario.email, linkConfirmacao)

        # cria o usuário no bd
        UsuarioBD.criar(usuario)

        return usuario.id

    # Envia um email para trocar de senha se o email estiver cadastrado no bd
    @staticmethod
    def recuperarConta(email: str, tasks: BackgroundTasks) -> None:
        try:
            UsuarioBD.buscar("email", email)
            # Gera o link e envia o email se o usuário estiver cadastrado
            link: str = geraLinkEsqueciSenha(email)
            tasks.add_task(enviarEmailResetSenha, email, link)  # Envia o email
        except NaoEncontradoExcecao:
            pass

    @staticmethod
    def trocarSenha(token: str, senha: str, tasks: BackgroundTasks) -> None:
        # Verifica o token e recupera o email
        email: str = processaTokenTrocaSenha(token)

        usuario: Usuario = UsuarioBD.buscar("email", email)

        if not ValidacaoCadastro.senha(senha):
            raise ValueError("Senha inválida")

        usuario.senha = hashSenha(senha)

        UsuarioBD.atualizar(usuario)

        tasks.add_task(enviarEmailAlteracaoDados, usuario.email, DadoAlterado.SENHA)

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
            if not usuario.emailConfirmado:
                raise EmailNaoConfirmadoExcecao()

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
    def getUsuarios() -> list[Usuario]:
        return UsuarioBD.listar()

    @staticmethod
    def getPetianos() -> list[Petiano]:
        petianos = []
        for petiano in UsuarioBD.listarPetianos():
            petianos.append(
                Petiano(
                    nome=petiano.nome,
                    github=petiano.github,
                    linkedin=petiano.linkedin,
                    instagram=petiano.instagram,
                    foto=f"{config.CAMINHO_BASE}/img/usuarios/{petiano.id}/foto",
                )
            )
        return petianos

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
    def editaSenha(
        dadosSenha: UsuarioAtualizarSenha, usuario: Usuario, tasks: BackgroundTasks
    ) -> None:
        """
        Atualiza a senha de um usuário existente caso a senha antiga seja correta.

        A atualização da conta pode não suceder por erro na validação de dados.
        """
        if conferirHashSenha(dadosSenha.senha.get_secret_value(), usuario.senha):
            usuario.senha = hashSenha(dadosSenha.novaSenha.get_secret_value())
            UsuarioBD.atualizar(usuario)
            tasks.add_task(enviarEmailAlteracaoDados, usuario.email, DadoAlterado.SENHA)

        else:
            raise APIExcecaoBase(message="Senha incorreta")

    @staticmethod
    def editarEmail(
        dadosEmail: UsuarioAtualizarEmail, id: str, tasks: BackgroundTasks
    ) -> None:
        """
        Atualiza o email de um usuário existente.

        Para UsuarioBD.atualizar o email, o usuário deve digitar sua senha atual.

        O usuário sempre é deslogado quando troca seu email, pois sua conta deve ser reativada.

        A atualização da conta pode não suceder por erro na validação de dados.
        """
        usuario = UsuarioControlador.getUsuario(id)

        if conferirHashSenha(dadosEmail.senha.get_secret_value(), usuario.senha):
            emailAntigo = usuario.email
            usuario.email = dadosEmail.novoEmail
            usuario.emailConfirmado = False

            UsuarioBD.atualizar(usuario)
            mensagemEmail: str = (
                f"{config.CAMINHO_BASE}/usuarios/confirma-email?token={geraTokenAtivaConta(usuario.id, usuario.email, timedelta(hours=24))}"
            )

            tasks.add_task(enviarEmailVerificacao, usuario.email, mensagemEmail)
            tasks.add_task(enviarEmailAlteracaoDados, emailAntigo, DadoAlterado.EMAIL)
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

        caminhoFotoPerfil = armazenaFotoUsuario(usuario.id, foto.file)
        if not caminhoFotoPerfil:
            raise ImagemNaoSalvaExcecao()

        usuario.foto = str(caminhoFotoPerfil)

        # atualiza no bd
        UsuarioBD.atualizar(usuario)

    @staticmethod
    def promoverPetiano(id: str) -> None:
        """
        Promove um usuário a petiano.
        """

        usuario = UsuarioControlador.getUsuario(id)

        logging.info(f"Promovendo usuário {usuario.id} a petiano")
        usuario.tipoConta = TipoConta.PETIANO

        UsuarioBD.atualizar(usuario)

        # desautentica o usuário para evitar que tokens antigas ganhem permissões novas
        TokenAutenticacaoBD.deletarTokensUsuario(id)

    @staticmethod
    def demitirPetiano(id: str, egresso: bool) -> None:
        """
        Demite um usuário petiano ou egresso a egresso, caso `egresso` seja verdadeiro, ou a estudante caso contrário.
        """

        usuario = UsuarioControlador.getUsuario(id)

        if (
            usuario.tipoConta != TipoConta.PETIANO
            and usuario.tipoConta != TipoConta.EGRESSO
        ):
            raise NaoAtualizadaExcecao(message="Usuário não é petiano nem egresso")

        if egresso:
            logging.info(f"Demitindo usuário {usuario.id} a egresso")
            usuario.tipoConta = TipoConta.EGRESSO
        else:
            logging.info(f"Demitindo usuário {usuario.id} a estudante")
            usuario.tipoConta = TipoConta.ESTUDANTE

        UsuarioBD.atualizar(usuario)

        # desautentica o usuário para forçar ressincronização
        TokenAutenticacaoBD.deletarTokensUsuario(id)

    @staticmethod
    def getHistoricoLogin(email: str) -> list[RegistroLogin]:
        """
        Retorna o histórico de logins do usuário.
        """
        return RegistroLoginBD.listarRegistrosUsuario(email)
