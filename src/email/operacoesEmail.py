import logging
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from enum import Enum

from src.config import config
from src.modelos.bd import EventoBD
from src.modelos.evento.evento import Evento
from src.modelos.excecao import EmailNaoFoiEnviadoExcecao
from src.modelos.inscrito.inscritoClad import TipoVaga


# Função para enviar email customizado
def enviarEmailGenerico(emailDestino: str, titulo: str, texto: str) -> None:
    """"
    Função para enviar email customizado. Para isso, é necessário os seguintes parâmetros:
        :emailDestino: str -> Email do destinatário.
        :titulo: str -> Título do email.
        :texto: str -> Texto do email.
    """
    mensagem: MIMEMultipart = MIMEMultipart()
    mensagem["From"] = config.EMAIL_SMTP
    mensagem["To"] = emailDestino
    mensagem["Subject"] = titulo
    mensagem.attach(MIMEText(texto, "plain", "utf-8"))

    return enviarEmail(emailDestino, mensagem)


# Função para enviar verificação de email
def enviarEmailVerificacao(emailDestino: str, link: str) -> None:
    """"
    Função para enviar email de verificação de email. Para isso, é necessário os seguintes parâmetros:
        :emailDestino: str -> Email do destinatário.
        :link: str -> Link para verificação do email.
    """
    mensagem: MIMEMultipart = MIMEMultipart()
    mensagem["From"] = config.EMAIL_SMTP
    mensagem["To"] = emailDestino
    mensagem["Subject"] = "PET-Info - Verficação de Conta"
    content = "Clique no link para verificar sua conta: " + link
    mensagem.attach(MIMEText(content, "plain", "utf-8"))

    return enviarEmail(emailDestino, mensagem)


# Função para enviar link troca de senha
def enviarEmailResetSenha(emailDestino: str, link: str) -> None:
    """"
    Função para enviar email de reset de senha. Para isso, é necessário os seguintes parâmetros:
        :emailDestino: str -> Email do destinatário.
        :link: str -> Link para reset de senha.
    """
    mensagem: MIMEMultipart = MIMEMultipart()
    mensagem["From"] = config.EMAIL_SMTP
    mensagem["To"] = emailDestino
    mensagem["Subject"] = "PET-Info - Reset de senha"
    mensagem.attach(
        MIMEText("Para resetar sua senha, acesse o link: " + link, "plain", "utf-8")
    )
    return enviarEmail(emailDestino, mensagem)


# Função que envia email para avisar sobre inscrição do evento
def enviarEmailConfirmacaoEvento(
    emailDestino: str,
    idEvento: str,
    tipoVaga: TipoVaga,
) -> None:
    """"
    Função para enviar email de confirmação de inscrição em evento. Para isso, é necessário os seguintes parâmetros:
        :emailDestino: str -> Email do destinatário.
        :idEvento: str -> ID do evento.
        :tipoVaga: TipoVaga -> Tipo de vaga escolhida pelo inscrito.

    Recupera o evento pelo ID e envia um email com as informações do evento e a vaga escolhida.
    """
    # Recupera o evento
    evento: Evento = EventoBD.buscar("_id", idEvento)

    mensagem: MIMEMultipart = MIMEMultipart()
    mensagem["From"] = config.EMAIL_SMTP
    mensagem["To"] = emailDestino
    mensagem["Subject"] = "PET-Info: Você foi cadastrado no evento " + evento.titulo

    diasEvento: str = ""
    for dia in evento.dias:
        diasEvento += (
            dia[0].strftime("%d/%m/%Y, %H:%M")
            + " - "
            + dia[1].strftime("%d/%m/%Y, %H:%M")
            + "\n"
        )

    if tipoVaga == TipoVaga.COM_NOTE:
        vaga = "Utilizar seu notebook."
    else:
        vaga = "Sem notebook."

    mensagem.attach(
        MIMEText(
            "Nome do evento: "
            + evento.titulo
            + "\nLocal do Evento: "
            + evento.local
            + "\nDias do evento: "
            + diasEvento
            + "\nNesse evento você optou por: "
            + vaga,
            "plain",
            "utf-8",
        )
    )

    return enviarEmail(emailDestino, mensagem)


class DadoAlterado(Enum):
    """""
    Enum para representar o tipo de dado a ser alterado
    """
    EMAIL = "email"
    SENHA = "senha"


# Função que envia email assim que senha/email forem trocados
def enviarEmailAlteracaoDados(emailDestino: str, dadoAlterado: DadoAlterado) -> None:
    """"
    Função para enviar email de confirmação de alteração de dados. Para isso, é necessário os seguintes parâmetros:
        :emailDestino: str -> Email do destinatário.
        :dadoAlterado: DadoAlterado -> Tipo de dado alterado.
    """
    mensagem: MIMEMultipart = MIMEMultipart()
    mensagem["From"] = config.EMAIL_SMTP
    mensagem["To"] = emailDestino
    mensagem["Subject"] = "PET-Info - Alteração de Dados"

    agora = datetime.now()
    horario_atual = agora.strftime("%H:%M")

    # Verifica o tipo de dado alterado e ajusta a mensagem de acordo
    if dadoAlterado == DadoAlterado.EMAIL:
        texto = "Seu email foi alterado com sucesso às " + horario_atual + "."
    else:  # dadoAlterado == DadoAlterado.SENHA:
        texto = "Sua senha foi alterada com sucesso às " + horario_atual + "."

    mensagem.attach(
        MIMEText(
            texto,
            "plain",
            "utf-8",
        )
    )
    return enviarEmail(emailDestino, mensagem)


# Função que faz o envio de emails
def enviarEmail(emailDestino: str, mensagem: MIMEMultipart) -> None:
    """"
    Função para enviar email. Para isso, é necessário os seguintes parâmetros:
        :emailDestino: str -> Email do destinatário.
        :mensagem: MIMEMultipart -> Mensagem a ser enviada.

    Essa função é chamada por outras funções desse arquivo, que preparam a mensagem a ser enviada.
    Quando o MOCK_EMAIL está ativado, a função apenas imprime o email no log, não enviando de fato.
    """
    if config.MOCK_EMAIL:
        logging.info("Envio de email para " + str(emailDestino) + "\n\n")

        # print MIME text with logging.info
        imprimir = {"text/plain", "text/html"}
        for part in mensagem.walk():
            if part.get_content_type() in imprimir:
                logging.info("Email:\n\n" + str(part.get_payload(decode=True)))

        return

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(config.EMAIL_SMTP, config.SENHA_SMTP)
            text = mensagem.as_string()
            server.sendmail(config.EMAIL_SMTP, emailDestino, text)
    except Exception as e:
        logging.warning("Erro ao enviar um email: " + str(e))
        raise (EmailNaoFoiEnviadoExcecao)
