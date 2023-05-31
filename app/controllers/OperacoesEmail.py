import ssl,smtplib
from email.message import EmailMessage

#Função para enviar email customizado
def enviarEmail(emailPet: str, senhaPet: str, emailDestino: str, titulo: str, texto: str) -> None: 
    m: EmailMessage = EmailMessage()
    m['From'] = emailPet
    m['To'] = emailDestino
    m['Subject'] = titulo
    m.set_content(texto)

    contexto: ssl.SSLContext = ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=contexto) as smtp:
        smtp.login(emailPet, senhaPet)
        smtp.sendmail(emailPet, emailDestino, m.as_string())

#Função para enviar verificação de email
def verificaEmail(emailPet: str, senhaPet: str, emailDestino: str, codigo: int) -> None:
    m: EmailMessage = EmailMessage()
    m['From'] = emailPet
    m['To'] = emailDestino
    m['Subject'] = "IDPetInfo - Código de Verficação"
    m.set_content("Seu código de verificação é: " + codigo)

    contexto: ssl.SSLContext = ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=contexto) as smtp:
        smtp.login(emailPet, senhaPet)
        smtp.sendmail(emailPet, emailDestino, m.as_string)

#Função para enviar link troca de senha
def resetarSenha(emailPet: str, senhaPet: str, emailDestino: str, link: str) -> None:
    m: EmailMessage = EmailMessage()
    m['From'] = emailPet
    m['To'] = emailDestino
    m['Subject'] = "Site PET-Info - Reset de senha"
    m.set_content("Para resetar sua senha, acesse o link: " + link)

    contexto: ssl.SSLContext = ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=contexto) as smtp:
        smtp.login(emailPet, senhaPet)
        smtp.sendmail(emailPet, emailDestino, m.as_string)
