import ssl, smtplib
from email.message import EmailMessage


# Função que envia email para avisar sobre inscrição do evento
def emailConfirmacaoEvento(
    emailPet: str,
    senhaPet: str,
    emailDestino: str,
    nomeEvento: str,
    localEvento: str,
    dataEvento: str,
    coindicoesEvento: str,
) -> None:
    mensagem: EmailMessage = EmailMessage()
    mensagem["From"] = emailPet
    mensagem["To"] = emailDestino
    mensagem["Subject"] = "PET-Info: Você foi cadastrado no evento" + nomeEvento
    mensagem.set_content(
        "Nome do evento: "
        + nomeEvento
        + "\nLocal do Evento: "
        + localEvento
        + "\nData do evento: "
        + dataEvento
        + "Nesse evento você optou por: "
        + coindicoesEvento
    )

    enviarEmail(
        emailPet,
        senhaPet,
        emailDestino,
    )


def enviarEmail(emailPet: str, senhaPet: str, emailDestino: str, mensagem: str) -> None:
    try:
        contexto: ssl.SSLContext = ssl.create_default_context()

        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=contexto) as smtp:
            smtp.login(emailPet, senhaPet)
            smtp.sendmail(emailPet, emailDestino, mensagem.as_string())

        print("Sucesso! O email foi enviado")
    except:
        print("Erro! Falha ao enviar email")
