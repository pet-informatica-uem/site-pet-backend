import smtplib
import ssl
from email.message import EmailMessage


# Função para enviar email customizado
def emailGenerico(
    emailPet: str, senhaPet: str, emailDestino: str, titulo: str, texto: str
):
    mensagem: EmailMessage = EmailMessage()
    mensagem["From"] = emailPet
    mensagem["To"] = emailDestino
    mensagem["Subject"] = titulo
    mensagem.set_content(texto)

    enviarEmail(emailPet, senhaPet, emailDestino, mensagem)


# Função para enviar verificação de email
def verificarEmail(emailPet: str, senhaPet: str, emailDestino: str, link: str):
    mensagem: EmailMessage = EmailMessage()
    mensagem["From"] = emailPet
    mensagem["To"] = emailDestino
    mensagem["Subject"] = "Pet-Info - Verficação de Conta"
    mensagem.set_content("Clique no link para verificar sua conta: " + link)

    enviarEmail(emailPet, senhaPet, emailDestino, mensagem)


# Função para enviar link troca de senha
def resetarSenha(emailPet: str, senhaPet: str, emailDestino: str, link: str):
    mensagem: EmailMessage = EmailMessage()
    mensagem["From"] = emailPet
    mensagem["To"] = emailDestino
    mensagem["Subject"] = "PET-Info - Reset de senha"
    mensagem.set_content("Para resetar sua senha, acesse o link: " + link)
    enviarEmail(emailPet, senhaPet, emailDestino, mensagem)


# Função que envia email para avisar sobre inscrição do evento
def emailConfirmacaoEvento(
    emailPet: str,
    senhaPet: str,
    emailDestino: str,
    evento: dict,
) -> dict:
    mensagem: EmailMessage = EmailMessage()
    mensagem["From"] = emailPet
    mensagem["To"] = emailDestino
    mensagem["Subject"] = (
        "PET-Info: Você foi cadastrado no evento " + evento["nome evento"]
    )

    mensagem.set_content(
        "Nome do evento: "
        + evento["nome evento"]
        + "\nLocal do Evento: "
        + evento["local"]
        + "\nData do evento: "
        + evento["data/hora evento"].strftime("%a %d %b %Y, %H:%M")
        + "\nNesse evento você optou por: "
        + evento["pré-requisitos"]
    )

    enviarEmail(emailPet, senhaPet, emailDestino, mensagem)


# Função que faz o envio de emails
def enviarEmail(
    emailPet: str, senhaPet: str, emailDestino: str, mensagem: EmailMessage
) -> None:
    contexto: ssl.SSLContext = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=contexto) as smtp:
        smtp.login(emailPet, senhaPet)
        smtp.sendmail(emailPet, emailDestino, mensagem.as_string())
