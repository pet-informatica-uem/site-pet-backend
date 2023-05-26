import ssl,smtplib
from email.message import EmailMessage

#Função para enviar email customizado
def enviarEmail(emailPet: str, senhaPet: str, emailDestino: str, titulo: str, texto: str) -> None: 
    m: EmailMessage = EmailMessage()
    m['From'] = emailPet
    m['To'] = emailDestino
    m['Subject'] = titulo
    m.set_content(texto)

    #Contexto é a configuração inicial para o envio de email, feita pela biblioteca smtp
    contexto: ssl.SSLContext = ssl.create_default_context()

    #Configura a variavel m da classe EmailMessage para enviar o email, utilizando a porta SSL da biblioteca, a porta 465 e o contexto
    #Efetua o envio do email
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=contexto) as smtp:
        smtp.login(emailPet, senhaPet)
        smtp.sendmail(emailPet, emailDestino, m.as_string())

#Função para enviar verificação de email
def verificaEmail(emailPet: str, senhaPet: str, emailDestino: str, codigo: int) -> None:
    #Registra na variável m (classe EmailMessage), os credenciais para envio do email (Remetente, destinatário, título, conteúdo)
    m: EmailMessage = EmailMessage()
    m['From'] = emailPet
    m['To'] = emailDestino
    m['Subject'] = "IDPetInfo - Código de Verficação"
    m.set_content("Seu código de verificação é: " + codigo)

    #Contexto é a configuração inicial para o envio de email, feita pela biblioteca smtp
    contexto: ssl.SSLContext = ssl.create_default_context()

    #Configura a variavel m da classe EmailMessage para enviar o email, utilizando a porta SSL da biblioteca, a porta 465 e o contexto
    #Efetua o envio do email
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=contexto) as smtp:
        smtp.login(emailPet, senhaPet)
        smtp.sendmail(emailPet, emailDestino, m.as_string)
