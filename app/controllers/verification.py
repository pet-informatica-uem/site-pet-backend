import ssl,smtplib
from email.message import EmailMessage
from random import choice
from datetime import datetime


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

#gerador de codigo aleatorio
def geradorAleatorio(emailUsuario: str):
    vetor = []
    caracteres = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
    for i in range(0, 22):
        c = choice(caracteres)
        vetor.append(c)
    codigo = ''.join(vetor)

    dataGeracao = datetime.now()
    verificar = {'Email': emailUsuario,
                 'Codigo': codigo,
                 'DataGeracao': dataGeracao}
    return verificar


# Enviar
def enviaCodigo(emailPet: str, senhaPet: str, emailDestino: str, codigo: str):
    titulo = "Verificação de conta"
    texto = f"Segue o código de verificação: {codigo}"
    enviarEmail(emailPet, senhaPet, emailDestino, titulo, texto)

# Armazenar email/codigo/tempo
def armanezarCodigo(verificar: dict):
    # Essa função armazenaria o codigo gerado no banco de dados
    pass

# Função para verificar o código com o armazenado e verificar o tempo
def verificarCodigo(emailEntrada: str, codigoEntrada: str) -> bool:
    tempoAgora = datetime.now()
    
    verificarBD = {'EmailBD': 'Email extraido do banco de dados',
                 'CodigoBD': 'Codigo extraido do banco de dados',
                 'DataBD': 'Data extraida do banco de dados'}
    
    # Realizar consulta a partir do email, se o email existir, retornar 1
    # Se o tempo expirou, reenviar outro codigo e alterar no BD, retornar 0
    # Comparar os códigos de entrada com os códigos no BD, se forem iguais, retornar 1

    # se tudo certo, retornar 1, senão, 0
    pass