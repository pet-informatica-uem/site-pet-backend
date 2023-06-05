import ssl, smtplib
from email.message import EmailMessage


# Função que envia email para avisar sobre inscrição do evento
def emailConfirmacaoEvento(
    emailPet: str,
    senhaPet: str,
    emailDestino: str,
    evento: dict,
) -> None:
    mensagem: EmailMessage = EmailMessage()
    mensagem["From"] = emailPet
    mensagem["To"] = emailDestino
    mensagem["Subject"] = (
        "PET-Info: Você foi cadastrado no evento" + evento["nomeEvento"]
    )
    mensagem.set_content(
        "Nome do evento: "
        + evento["nomeEvento"]
        + "\nLocal do Evento: "
        + evento["localEvento"]
        + "\nData do evento: "
        + evento["dataEvento"]
        + "Nesse evento você optou por: "
        + evento["coindicoesEvento"]
    )

    enviarEmail(emailPet, senhaPet, emailDestino, mensagem)


def enviarEmail(emailPet: str, senhaPet: str, emailDestino: str, mensagem: str) -> str:
    try:
        contexto: ssl.SSLContext = ssl.create_default_context()

        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=contexto) as smtp:
            smtp.login(emailPet, senhaPet)
            smtp.sendmail(emailPet, emailDestino, mensagem.as_string())

        return {"mensagem": "Email enviado com sucesso", "status": "200"}
    except:
        return {"mensagem": "Falha ao enviar o email", "status": "400"}
