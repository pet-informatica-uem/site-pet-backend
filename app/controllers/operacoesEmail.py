import ssl, smtplib
from email.message import EmailMessage


# Função para enviar email customizado
def emailGenerico(
    emailPet: str, senhaPet: str, emailDestino: str, titulo: str, texto: str
) -> dict:
    mensagem: EmailMessage = EmailMessage()
    mensagem["From"] = emailPet
    mensagem["To"] = emailDestino
    mensagem["Subject"] = titulo
    mensagem.set_content(texto)

    return enviarEmail(emailPet, senhaPet, emailDestino, mensagem)


# Função para enviar verificação de email
def verificarEmail(emailPet: str, senhaPet: str, emailDestino: str, link: str) -> dict:
    mensagem: EmailMessage = EmailMessage()
    mensagem["From"] = emailPet
    mensagem["To"] = emailDestino
    mensagem["Subject"] = "Pet-Info - Verficação de Conta"
    mensagem.set_content("Clique no link para verificar sua conta: " + link)

    return enviarEmail(emailPet, senhaPet, emailDestino, mensagem)


# Função para enviar link troca de senha
def resetarSenha(emailPet: str, senhaPet: str, emailDestino: str, link: str) -> dict:
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
    evento: dict,
) -> dict:
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

    return enviarEmail(emailPet, senhaPet, emailDestino, mensagem)


# Função que faz o envio de emails
def enviarEmail(
    emailPet: str, senhaPet: str, emailDestino: str, mensagem: EmailMessage
) -> dict:
    try:
        contexto: ssl.SSLContext = ssl.create_default_context()

        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=contexto) as smtp:
            smtp.login(emailPet, senhaPet)
            smtp.sendmail(emailPet, emailDestino, mensagem.as_string())

        return {"mensagem": "Email enviado com sucesso", "status": "200"}
    except:
        return {"mensagem": "Falha ao enviar o email", "status": "400"}
