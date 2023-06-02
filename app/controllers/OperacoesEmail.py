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
    m: EmailMessage = EmailMessage()
    m["From"] = emailPet
    m["To"] = emailDestino
    m["Subject"] = "PET-Info: Você foi cadastrado no evento" + nomeEvento
    m.set_content(
        "Nome do evento: "
        + nomeEvento
        + "\nLocal do Evento: "
        + localEvento
        + "\nData do evento: "
        + dataEvento
        + "Nesse evento você optou por: "
        + coindicoesEvento
    )

    contexto: ssl.SSLContext = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=contexto) as smtp:
        smtp.login(emailPet, senhaPet)
        smtp.sendmail(emailPet, emailDestino, m.as_string)
