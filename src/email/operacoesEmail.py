import logging
import smtplib
from datetime import datetime
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from enum import Enum
from html import escape

from src.config import config
from src.modelos.bd import EventoBD
from src.modelos.evento.evento import Evento
from src.modelos.excecao import EmailNaoFoiEnviadoExcecao
from src.modelos.evento.eventoClad import TipoVaga
from src.autenticacao.jwtoken import geraTokenPresencaEvento
from src.img.operacoesQrCode import geraQRCode


# Função para enviar email customizado
def enviarEmailGenerico(emailDestino: str, titulo: str, texto: str) -> None:
    """
    Envia um e-mail ao destino com o título e texto fornecidos, utilizando
    a conta de e-mail configurada no arquivo de configuração.

        :param emailDestino: E-mail do destinatário.
        :param titulo: Título do e-mail.
        :param texto: Texto do e-mail.
    """
    mensagem: MIMEMultipart = MIMEMultipart()
    mensagem["From"] = config.EMAIL_SMTP
    mensagem["To"] = emailDestino
    mensagem["Subject"] = titulo
    mensagem.attach(MIMEText(texto, "plain", "utf-8"))

    return enviarEmail(emailDestino, mensagem)


# Função para enviar verificação de email
def enviarEmailVerificacao(emailDestino: str, link: str) -> None:
    """
    Envia um e-mail ao destino com um link para verificação da conta.

        :param emailDestino: Email do destinatário.
        :param link: Link para verificação do e-mail.
    """
    mensagem: MIMEMultipart = MIMEMultipart()
    mensagem["From"] = config.EMAIL_SMTP
    mensagem["To"] = emailDestino
    mensagem["Subject"] = "PET-Info - Verficação de Conta"
    content = "Clique no link para verificar sua conta: " + link
    mensagem.attach(MIMEText(content, "plain", "utf-8"))

    return enviarEmail(emailDestino, mensagem)


# Função para enviar link troca de senha
def enviarEmailResetSenha(emailDestino: str, link: str) -> None:
    """
    Envia um e-mail contendo um link para redefinição de senha ao destinatário.
    
        :param emailDestino: E-mail do destinatário.
        :param link: Link para redefinição da senha.
    """
    mensagem: MIMEMultipart = MIMEMultipart()
    mensagem["From"] = config.EMAIL_SMTP
    mensagem["To"] = emailDestino
    mensagem["Subject"] = "PET-Info - Reset de senha"
    mensagem.attach(
        MIMEText("Para resetar sua senha, acesse o link: " + link, "plain", "utf-8")
    )
    return enviarEmail(emailDestino, mensagem)


# Função que envia email para avisar sobre inscrição do evento
def enviarEmailConfirmacaoEvento(
    emailDestino: str,
    idEvento: str,
    idUsuario: str,
    tipoVaga: TipoVaga,
) -> None:
    """
    Envia um e-mail ao destinatário informando a sua inscrição em um evento, contendo
    informações sobre o evento e a vaga escolhida.

    As informações do evento são recuperadas do banco de dados pelo identificador.

        :param emailDestino: E-mail do destinatário.
        :param idEvento: Identificador único do evento.
        :param tipoVaga: Tipo de vaga escolhida pelo inscrito.
    """
    # Recupera o evento
    evento: Evento = EventoBD.buscar("_id", idEvento)

    token_presenca = geraTokenPresencaEvento(idEvento, idUsuario)
    qrCode = geraQRCode(token_presenca)

    # A mensagem é do tipo "related" para que a imagem do QR Code possa ser
    # referenciada pelo HTML através do seu Content-ID.
    mensagem: MIMEMultipart = MIMEMultipart("related")
    mensagem["From"] = config.EMAIL_SMTP
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

    textoSimples: str = (
        "Nome do evento: "
        + evento.titulo
        + "\nLocal do Evento: "
        + evento.local
        + "\nDias do evento: "
        + diasEvento
        + "\nNesse evento você optou por: "
        + vaga
        + "\n\nApresente o QR Code em anexo na entrada do evento para registrar sua presença."
    )

    textoHtml: str = geraHtmlConfirmacaoEvento(
        titulo=evento.titulo,
        local=evento.local,
        diasEvento=diasEvento,
        vaga=vaga,
    )

    # As duas versões do corpo (texto puro e HTML) são alternativas entre si:
    # o cliente de e-mail exibe a última que conseguir renderizar.
    corpo: MIMEMultipart = MIMEMultipart("alternative")
    corpo.attach(MIMEText(textoSimples, "plain", "utf-8"))
    corpo.attach(MIMEText(textoHtml, "html", "utf-8"))
    mensagem.attach(corpo)

    # Imagem embutida, referenciada no HTML por "cid:qrcode".
    imagemQrCode: MIMEImage = MIMEImage(qrCode, "png")
    imagemQrCode.add_header("Content-ID", "<qrcode>")
    imagemQrCode.add_header("Content-Disposition", "inline", filename="qrcode.png")
    mensagem.attach(imagemQrCode)

    return enviarEmail(emailDestino, mensagem)


def geraHtmlConfirmacaoEvento(
    titulo: str, local: str, diasEvento: str, vaga: str
) -> str:
    """
    Monta o corpo HTML do e-mail de confirmação de inscrição em um evento.

    A imagem do QR Code não é embutida no HTML: ela é referenciada por
    `cid:qrcode`, e deve ser anexada à mensagem com esse mesmo Content-ID.

        :param titulo: Título do evento.
        :param local: Local do evento.
        :param diasEvento: Dias do evento, separados por quebras de linha.
        :param vaga: Descrição do tipo de vaga escolhido.
        :return: Corpo do e-mail em HTML.
    """
    # Escapa o conteúdo vindo do banco e converte as quebras de linha dos dias
    # do evento em <br>, já que o HTML ignora "\n".
    titulo = escape(titulo)
    local = escape(local)
    vaga = escape(vaga)
    diasEventoHtml: str = "<br>".join(
        escape(dia) for dia in diasEvento.strip().split("\n")
    )

    return f"""\
<html>
  <body style="margin: 0; padding: 0; background-color: #f4f4f4;
               font-family: Arial, Helvetica, sans-serif; color: #333333;">
    <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%"
           style="background-color: #f4f4f4; padding: 24px 12px;">
      <tr>
        <td align="center">
          <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="600"
                 style="max-width: 600px; width: 100%; background-color: #ffffff;
                        border-radius: 8px; overflow: hidden;">
            <tr>
              <td style="background-color: #1b3a6b; padding: 20px 24px;">
                <h1 style="margin: 0; font-size: 20px; color: #ffffff;">PET-Informática UEM</h1>
              </td>
            </tr>
            <tr>
              <td style="padding: 24px;">
                <p style="margin: 0 0 16px 0; font-size: 18px;">
                  Sua inscrição no evento <strong>{titulo}</strong> foi confirmada!
                </p>

                <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%"
                       style="font-size: 16px; margin-bottom: 24px;">
                  <tr>
                    <td style="padding: 6px 0; width: 140px; vertical-align: top;"><strong>Evento</strong></td>
                    <td style="padding: 6px 0;">{titulo}</td>
                  </tr>
                  <tr>
                    <td style="padding: 6px 0; vertical-align: top;"><strong>Local</strong></td>
                    <td style="padding: 6px 0;">{local}</td>
                  </tr>
                  <tr>
                    <td style="padding: 6px 0; vertical-align: top;"><strong>Dias</strong></td>
                    <td style="padding: 6px 0;">{diasEventoHtml}</td>
                  </tr>
                  <tr>
                    <td style="padding: 6px 0; vertical-align: top;"><strong>Sua opção</strong></td>
                    <td style="padding: 6px 0;">{vaga}</td>
                  </tr>
                </table>

                <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%"
                       style="background-color: #f7f9fc; border: 1px solid #e1e6ef;
                              border-radius: 8px;">
                  <tr>
                    <td align="center" style="padding: 20px;">
                      <p style="margin: 0 0 12px 0; font-size: 15px;">
                        <strong>Apresente este QR Code na entrada do evento</strong>
                      </p>
                      <!-- O QR Code do token é denso; abaixo de ~260px a leitura
                           na tela fica difícil. -->
                      <img src="cid:qrcode" alt="QR Code de presença no evento"
                           width="260" height="260"
                           style="display: block; width: 260px; height: 260px;
                                  border: 0; background-color: #ffffff;">
                      <p style="margin: 12px 0 0 0; font-size: 12px; color: #666666;">
                        Ele é pessoal e será usado para registrar a sua presença.
                      </p>
                    </td>
                  </tr>
                </table>
              </td>
            </tr>
            <tr>
              <td style="background-color: #f4f4f4; padding: 16px 24px;
                         font-size: 12px; color: #777777;">
                Este e-mail foi enviado automaticamente. Não é necessário respondê-lo.
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
  </body>
</html>
"""


class DadoAlterado(Enum):
    """""
    Qual dado foi alterado no perfil do usuário.
    """
    EMAIL = "email"
    SENHA = "senha"


# Função que envia email assim que senha/email forem trocados
def enviarEmailAlteracaoDados(emailDestino: str, dadoAlterado: DadoAlterado) -> None:
    """
    Envia um e-mail ao destinatário informando de alterações feitas em seu perfil.
        :param emailDestino: E-mail do destinatário.
        :param dadoAlterado: Tipo de dado alterado.
    """
    mensagem: MIMEMultipart = MIMEMultipart()
    mensagem["From"] = config.EMAIL_SMTP
    mensagem["To"] = emailDestino
    mensagem["Subject"] = "PET-Info - Alteração de Dados"

    agora = datetime.now()
    horario_atual = agora.strftime("%H:%M")

    # Verifica o tipo de dado alterado e ajusta a mensagem de acordo
    if dadoAlterado == DadoAlterado.EMAIL:
        texto = "Seu email foi alterado com sucesso às " + horario_atual + "."
    else:  # dadoAlterado == DadoAlterado.SENHA:
        texto = "Sua senha foi alterada com sucesso às " + horario_atual + "."

    mensagem.attach(
        MIMEText(
            texto,
            "plain",
            "utf-8",
        )
    )
    return enviarEmail(emailDestino, mensagem)


# Função que faz o envio de emails
def enviarEmail(emailDestino: str, mensagem: MIMEMultipart) -> None:
    """
    Envia um e-mail ao destinatário com a mensagem fornecida.

    Essa função é chamada por outras funções desse arquivo, que preparam a mensagem a ser enviada.
    Quando o MOCK_EMAIL está ativado, a função apenas imprime o e-mail no log, não enviando de fato.

        :param emailDestino: E-mail do destinatário.
        :param mensagem: Mensagem a ser enviada.

    """
    if config.MOCK_EMAIL:
        logging.info("Envio de e-mail para " + str(emailDestino) + "\n\n")

        # print MIME text with logging.info
        imprimir = {"text/plain", "text/html"}
        for part in mensagem.walk():
            if part.get_content_type() in imprimir:
                logging.info("Email:\n\n" + str(part.get_payload(decode=True)))

        return

    try:
        with smtplib.SMTP(config.SERVIDOR_SMTP, config.PORTA_SMTP) as server:
            if config.SMTP_TLS:
                server.starttls()
            server.login(config.EMAIL_SMTP, config.SENHA_SMTP)
            text = mensagem.as_string()
            server.sendmail(config.EMAIL_SMTP, emailDestino, text)
    except Exception as e:
        logging.warning("Erro ao enviar um email: " + str(e))
        raise (EmailNaoFoiEnviadoExcecao)