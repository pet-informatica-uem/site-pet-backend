"""
Controladores para rotas de gerenciamento de usuários.
"""

from enum import StrEnum
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
from src.modelos.bd import RegistroLoginBD, TokenAutenticacaoBD, UsuarioBD, EventoBD, cliente
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
from src.modelos.usuario.usuario import Petiano, TipoConta, EventosInscrito, Usuario
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
        Recebe um token de ativação de conta e ativa a conta associada ao token, caso válido.

        :param token: token JWT de ativação de conta.
        
        :raises TokenInvalidoExcecao: Se o token for inválido.
        :raises UsuarioNaoEncontradoExcecao: Se o usuário associado ao token não for encontrado.
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
        Cria uma conta com os dados `dadosUsuario` fornecidos, e envia um email
        de confirmação de criação de conta ao endereço fornecido.
        
        Um objeto `BackgroundTasks` deve ser fornecido para o envio do email.

            A criação da conta pode não suceder por erro na validação de dados,
            por já haver uma conta cadastrada com tal CPF ou email ou por falha
            de conexão com o banco de dados.
        
        :param dadosUsuario: Dados do usuário a serem cadastrados.
        :param tasks: Objeto `BackgroundTasks` para envio de email.

        :return id: ID do usuário criado.
        :raises JaExisteExcecao: Se já houver uma conta cadastrada com o CPF ou email fornecidos.
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
        """
        Envia um email de recuperação de senha para o endereço fornecido, se o endereço
        estiver associado a uma conta cadastrada. Se o endereço não estiver associado a
        uma conta, a função não faz nada.

        :param email: Endereço de email associado à conta.
        :param tasks: Objeto `BackgroundTasks` para envio de email.
        """
        try:
            UsuarioBD.buscar("email", email)
            # Gera o link e envia o email se o usuário estiver cadastrado
            link: str = geraLinkEsqueciSenha(email)
            tasks.add_task(enviarEmailResetSenha, email, link)  # Envia o email
        except NaoEncontradoExcecao:
            pass

    @staticmethod
    def trocarSenha(token: str, senha: str, tasks: BackgroundTasks) -> None:
        """
        Realiza a troca de senha de um usuário com o token JWT de troca de senha fornecido.
        O usuário tem sua senha alterada para a senha fornecida.

        :param token: Token JWT de troca de senha.
        :param senha: Nova senha do usuário.
        :param tasks: Objeto `BackgroundTasks` para envio de email.

        :raises ValueError: Se a senha fornecida for inválida.
        :raises TokenInvalidoExcecao: Se o token fornecido for inválido.
        :raises NaoEncontradoExcecao: Se não houver um usuário associado ao token fornecido.
        """
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
        Verifica se o email e senha fornecidos correspondem a um usuário cadastrado e ativo e
        retorna um novo token de autenticação, neste caso.

        :param email: Email do usuário.
        :param senha: Senha do usuário a ser conferida.

        :return: Dicionário contendo o token de autenticação, com os campos `access_token`
        contendo o token e `token_type` = "bearer".

        :raises EmailSenhaIncorretoExcecao: Se o email ou senha fornecidos estiverem incorretos,
        ou se o usuário não estiver ativo ou não existir.
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

        :param token: Token de autenticação do usuário.
        :return usuario: Dados do usuário autenticado.
        :raises NaoAutenticadoExcecao: Se o token fornecido for inválido ou se o usuário não existir.
        :raises EmailNaoConfirmadoExcecao: Se o email do usuário associado ao token não estiver confirmado.
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

        :param id: ID do usuário a ser obtido.
        :return usuario: Dados do usuário.
        :raises UsuarioNaoEncontradoExcecao: Se o usuário com o ID fornecido não existir.
        """

        if usuario := UsuarioBD.buscar("_id", id):
            return usuario

        raise UsuarioNaoEncontradoExcecao()

    @staticmethod
    def getUsuarios() -> list[Usuario]:
        """
        Retorna uma lista de todos os usuários cadastrados.

        :return usuarios: Lista de usuários.
        """
        return UsuarioBD.listar()

    @staticmethod
    def getPetianos() -> list[Petiano]:
        """
        Retorna uma lista de todos os petianos cadastrados.

        :return petianos: Lista de petianos.
        """
        petianos = []
        for petiano in UsuarioBD.listarPetianos():
            # define a url da foto do petiano
            urlFoto = None
            if petiano.foto:
                urlFoto = f"{config.CAMINHO_BASE}/img/usuarios/{petiano.id}/foto"
            
            # adiciona o petiano à lista
            petianos.append(
                Petiano(
                    id=petiano.id,
                    nome=petiano.nome,
                    github=petiano.github,
                    linkedin=petiano.linkedin,
                    instagram=petiano.instagram,
                    foto=urlFoto,
                    inicioPet=petiano.inicioPet,
                    fimPet=petiano.fimPet,
                    sobre=petiano.sobre,
                    eventosInscrito=petiano.eventosInscrito,
                    tipoConta=petiano.tipoConta,
                    apadrinhadoPor=petiano.apadrinhadoPor,
                )
            )
        return petianos

    @staticmethod
    def getPetianosAndEgressos() -> list[Petiano]:
        """
        Retorna uma lista de todos os petianos e egressos cadastrados.

        :return petianos: Lista de petianos e egressos.
        """
        petianos = []
        for petiano in UsuarioBD.listarPetianosAndEgressos():
            # define a url da foto do petiano ou egresso
            urlFoto = None
            if petiano.foto:
                urlFoto = f"{config.CAMINHO_BASE}/img/usuarios/{petiano.id}/foto"

            # transforma os IDs em objetos EventosInscrito
            eventos: list[EventosInscrito] = []

            for evento_id in petiano.eventosInscrito:
                try:
                    ev: Evento = EventoBD.buscar("_id", evento_id)

                    eventos.append(
                        EventosInscrito(titulo=ev.titulo, arte=f"{config.CAMINHO_BASE}/img/eventos/{ev.id}/arte")
                    )
                except Exception as e:
                    print("Evento não encontrado:", e)

            # adiciona o petiano ou egresso à lista
            petianos.append(
                Petiano(
                    id=petiano.id,
                    nome=petiano.nome,
                    github=petiano.github,
                    linkedin=petiano.linkedin,
                    instagram=petiano.instagram,
                    foto=urlFoto,
                    inicioPet=petiano.inicioPet,
                    fimPet=petiano.fimPet,
                    sobre=petiano.sobre,
                    eventosInscrito=eventos,
                    tipoConta=petiano.tipoConta,
                    apadrinhadoPor=petiano.apadrinhadoPor,
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

        :param id: ID do usuário a ser atualizado.
        :param dadosUsuario: Dados do usuário a serem atualizados.
        :return usuario: Dados do usuário atualizados.
        :raises UsuarioNaoEncontradoExcecao: Se o usuário com o ID fornecido não existir.
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
    def deletarUsuario(id: str) -> None:
        """
        Deleta um usuário existente (*hard delete*).

        :param id: ID do usuário a ser deletado.
        :raises UsuarioNaoEncontradoExcecao: Se o usuário com o ID fornecido não existir.
        """
        UsuarioControlador.getUsuario(id)

        UsuarioBD.deletar(id)

    @staticmethod
    def editaSenha(
        dadosSenha: UsuarioAtualizarSenha, usuario: Usuario, tasks: BackgroundTasks
    ) -> None:
        """
        Atualiza a senha de um usuário existente caso a senha antiga seja correta.
        Causa um envio de email de confirmação de alteração de senha.

        A atualização da conta pode não suceder por erro na validação de dados.

        :param dadosSenha: Dados de senha a serem atualizados.
        :param usuario: Usuário a ser atualizado.
        :param tasks: Objeto `BackgroundTasks` para envio de email.

        :raises NaoAutenticadoExcecao: Se a senha antiga fornecida estiver incorreta.
        """
        if conferirHashSenha(dadosSenha.senha.get_secret_value(), usuario.senha):
            usuario.senha = hashSenha(dadosSenha.novaSenha.get_secret_value())
            UsuarioBD.atualizar(usuario)
            tasks.add_task(enviarEmailAlteracaoDados, usuario.email, DadoAlterado.SENHA)

        else:
            raise NaoAutenticadoExcecao(message="Senha incorreta")

    @staticmethod
    def editarEmail(
        dadosEmail: UsuarioAtualizarEmail, id: str, tasks: BackgroundTasks
    ) -> None:
        """
        Atualiza o email de um usuário existente.

        Para UsuarioBD.atualizar o email, o usuário deve digitar sua senha atual.

        O usuário sempre é deslogado quando troca seu email, pois sua conta deve ser reativada.

        A atualização da conta pode não suceder por erro na validação de dados.

        :param dadosEmail: Dados de email a serem atualizados.
        :param id: ID do usuário a ser atualizado.
        :param tasks: Objeto `BackgroundTasks` para envio de email.
        :raises NaoAutenticadoExcecao: Se a senha fornecida estiver incorreta.
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
            raise NaoAutenticadoExcecao(message="Senha incorreta")

    @staticmethod
    def editarFoto(usuario: Usuario, foto: UploadFile) -> None:
        """
        Atualiza a foto de perfil de um usuário existente.

        Para UsuarioBD.atualizar a foto, o usuário deve inserir uma foto.

        A atualização da conta pode não suceder por erro na validação de dados.

        :param usuario: Usuário a ser atualizado.
        :param foto: Foto a ser atualizada.
        :raises ImagemInvalidaExcecao: Se a imagem fornecida for inválida.
        :raises ImagemNaoSalvaExcecao: Se a imagem fornecida não puder ser salva.
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
        Promove um usuário a petiano (altera seu tipo de conta para TipoConta.PETIANO).

        :param id: Id do usuário a ser promovido.
        :raises UsuarioNaoEncontradoExcecao: Se o usuário com o id fornecido não existir.
        """

        usuario = UsuarioControlador.getUsuario(id)

        logging.info(f"Promovendo usuário {usuario.id} a petiano")
        usuario.tipoConta = TipoConta.PETIANO

        UsuarioBD.atualizar(usuario)

        # desautentica o usuário para evitar que tokens antigas ganhem permissões novas
        TokenAutenticacaoBD.deletarTokensUsuario(id)
    
    class DemitirPetianoPara(StrEnum):
        """
        Tipo de demissão de petiano.
        """

        ESTUDANTE = "estudante"
        """
        Demite um petiano a estudante.
        """

        EGRESSO = "egresso"
        """
        Demite um petiano a egresso.
        """

    @staticmethod
    def demitirPetiano(id: str, egresso: DemitirPetianoPara) -> None:
        """
        Demite um usuário petiano ou egresso a egresso, caso `egresso` seja verdadeiro, ou a estudante caso contrário.

        :param id: Id do usuário a ser demitido.
        :param egresso: Se verdadeiro, demite o usuário a egresso; caso contrário, demite a estudante.
        :raises UsuarioNaoEncontradoExcecao: Se o usuário com o id fornecido não existir.
        :raises NaoAtualizadaExcecao: Se o usuário não for petiano nem egresso.
        """

        usuario = UsuarioControlador.getUsuario(id)

        if (
            usuario.tipoConta != TipoConta.PETIANO
            and usuario.tipoConta != TipoConta.EGRESSO
        ):
            raise NaoAtualizadaExcecao(message="Usuário não é petiano nem egresso")

        if egresso == UsuarioControlador.DemitirPetianoPara.EGRESSO:
            logging.info(f"Demitindo usuário {usuario.id} a egresso")
            usuario.tipoConta = TipoConta.EGRESSO
        elif egresso == UsuarioControlador.DemitirPetianoPara.ESTUDANTE:
            logging.info(f"Demitindo usuário {usuario.id} a estudante")
            usuario.tipoConta = TipoConta.ESTUDANTE

        UsuarioBD.atualizar(usuario)

        # desautentica o usuário para forçar ressincronização
        TokenAutenticacaoBD.deletarTokensUsuario(id)

    @staticmethod
    def getHistoricoLogin(email: str) -> list[RegistroLogin]:
        """
        Retorna o histórico de logins do usuário com o email fornecido.

        :param email: Email do usuário.
        :return historico: Lista de registros de login.
        """
        return RegistroLoginBD.listarRegistrosUsuario(email)
    


