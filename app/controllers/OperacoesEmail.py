import ssl, smtplib
from email.message import EmailMessage


# Função para enviar email customizado
def emailGenerico(
    emailPet: str, senhaPet: str, emailDestino: str, titulo: str, texto: str
) -> None:
    mensagem: EmailMessage = EmailMessage()
    mensagem["From"] = emailPet
    mensagem["To"] = emailDestino
    mensagem["Subject"] = titulo
    mensagem.set_content(texto)

    enviarEmail(emailPet, senhaPet, emailDestino, mensagem)


# Função para enviar verificação de email
def verificarEmail(
    emailPet: str, senhaPet: str, emailDestino: str, codigo: str
) -> None:
    mensagem: EmailMessage = EmailMessage()
    mensagem["From"] = emailPet
    mensagem["To"] = emailDestino
    mensagem["Subject"] = "Pet-Info - Código de Verficação"
    mensagem.set_content("Seu código de verificação é: " + codigo)

    enviarEmail(emailPet, senhaPet, emailDestino, mensagem)


# Função para enviar link troca de senha
def resetarSenha(emailPet: str, senhaPet: str, emailDestino: str, link: str) -> None:
    mensagem: EmailMessage = EmailMessage()
    mensagem["From"] = emailPet
    mensagem["To"] = emailDestino
    mensagem["Subject"] = "PET-Info - Reset de senha"
    mensagem.set_content("Para resetar sua senha, acesse o link: " + link)

    enviarEmail(emailPet, senhaPet, emailDestino, mensagem)


def enviarEmail(emailPet: str, senhaPet: str, emailDestino: str, mensagem: str) -> None:
    try:
        contexto: ssl.SSLContext = ssl.create_default_context()

        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=contexto) as smtp:
            smtp.login(emailPet, senhaPet)
            smtp.sendmail(emailPet, emailDestino, mensagem.as_string())
    except:
        print("Erro! Falha ao enviar email")
