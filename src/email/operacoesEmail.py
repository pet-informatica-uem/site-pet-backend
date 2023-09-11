import smtplib
import ssl
from email.message import EmailMessage

from src.modelos.bd import EventoBD
from src.modelos.evento.evento import Evento
from src.modelos.excecao import EmailNaoFoiEnviadoExcecao
from src.modelos.inscrito.inscritoClad import TipoVaga


# Função para enviar email customizado
def emailGenerico(
    emailPet: str, senhaPet: str, emailDestino: str, titulo: str, texto: str
) -> None:
    mensagem: EmailMessage = EmailMessage()
    mensagem["From"] = emailPet
    mensagem["To"] = emailDestino
    mensagem["Subject"] = titulo
    mensagem.set_content(texto)

    return enviarEmail(emailPet, senhaPet, emailDestino, mensagem)


# Função para enviar verificação de email
def verificarEmail(emailPet: str, senhaPet: str, emailDestino: str, link: str) -> None:
    mensagem: EmailMessage = EmailMessage()
    mensagem["From"] = emailPet
    mensagem["To"] = emailDestino
    mensagem["Subject"] = "Pet-Info - Verficação de Conta"
    mensagem.set_content("Clique no link para verificar sua conta: " + link)

    return enviarEmail(emailPet, senhaPet, emailDestino, mensagem)


# Função para enviar link troca de senha
def resetarSenha(emailPet: str, senhaPet: str, emailDestino: str, link: str) -> None:
    mensagem: EmailMessage = EmailMessage()
    mensagem["From"] = emailPet
    mensagem["To"] = emailDestino
    mensagem["Subject"] = "PET-Info - Reset de senha"
    mensagem.set_content("Para resetar sua senha, acesse o link: " + link)
    return enviarEmail(emailPet, senhaPet, emailDestino, mensagem)


# Função que envia email para avisar sobre inscrição do evento
def emailConfirmacaoEvento(
    emailPet: str,
    senhaPet: str,
    emailDestino: str,
    idEvento: str,
    tipoVaga: TipoVaga,
) -> None:
    # Recupera o evento
    evento: Evento = EventoBD.buscar("_id", idEvento)

    mensagem: EmailMessage = EmailMessage()
    mensagem["From"] = emailPet
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

    mensagem.set_content(
        "Nome do evento: "
        + evento.titulo
        + "\nLocal do Evento: "
        + evento.local
        + "\nDias do evento: "
        + diasEvento
        + "\nNesse evento você optou por: "
        + vaga
    )

    return enviarEmail(emailPet, senhaPet, emailDestino, mensagem)


# Função que faz o envio de emails
def enviarEmail(
    emailPet: str, senhaPet: str, emailDestino: str, mensagem: EmailMessage
) -> None:
    try:
        contexto: ssl.SSLContext = ssl.create_default_context()

        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=contexto) as smtp:
            smtp.login(emailPet, senhaPet)
            smtp.sendmail(emailPet, emailDestino, mensagem.as_string())
    except Exception as e:
        raise EmailNaoFoiEnviadoExcecao()
