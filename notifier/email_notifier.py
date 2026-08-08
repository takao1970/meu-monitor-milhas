import smtplib
import sys
import os
from email.mime.text import MIMEText

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import EMAIL_REMETENTE, EMAIL_SENHA_APP, EMAIL_DESTINATARIO

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587

MENSAGEM_TEMPLATE = """Promoção de Milhas Encontrada!

{titulo}

De: {programa_origem}
Para: {programa_destino}
Bônus máximo: {bonus_max}%
CPM (máximo): R$ {cpm:.2f}

Ver regulamento: {url}
"""


def formatar_mensagem(
    titulo: str,
    programa_origem: str,
    programa_destino: str,
    bonus_max: float,
    cpm: float,
    url: str,
) -> str:
    return MENSAGEM_TEMPLATE.format(
        titulo=titulo,
        programa_origem=programa_origem,
        programa_destino=programa_destino,
        bonus_max=bonus_max,
        cpm=cpm,
        url=url,
    )


def enviar_alerta(mensagem: str, assunto: str = "🚨 Promoção de Milhas Encontrada"):
    """Envia o alerta por e-mail via SMTP do Gmail (requer senha de app)."""
    email_msg = MIMEText(mensagem, "plain", "utf-8")
    email_msg["Subject"] = assunto
    email_msg["From"] = EMAIL_REMETENTE
    email_msg["To"] = EMAIL_DESTINATARIO

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
        smtp.starttls()
        smtp.login(EMAIL_REMETENTE, EMAIL_SENHA_APP)
        smtp.sendmail(EMAIL_REMETENTE, EMAIL_DESTINATARIO, email_msg.as_string())


if __name__ == "__main__":
    enviar_alerta("✅ Monitor de milhas configurado com sucesso!", assunto="Teste - Monitor de Milhas")
