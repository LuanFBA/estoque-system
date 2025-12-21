import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings


def send_email(to: str, subject: str, body: str) -> bool:
    if not settings.smtp_host:
        print("[email_service] SMTP não configurado, email não enviado.")
        return False

    try:
        msg = MIMEMultipart()
        msg["From"] = settings.smtp_from
        msg["To"] = to
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            if settings.smtp_tls:
                server.starttls()
            if settings.smtp_user and settings.smtp_password:
                server.login(settings.smtp_user, settings.smtp_password)
            server.sendmail(settings.smtp_from, to, msg.as_string())

        print(f"[email_service] Email enviado para {to}")
        return True
    except Exception as exc:
        print(f"[email_service] Erro ao enviar email: {exc}")
        return False


def send_order_processed_email(order_id: int, to: str) -> bool:
    subject = f"Pedido #{order_id} processado com sucesso"
    body = f"""Olá!

Seu pedido #{order_id} foi processado com sucesso.

Obrigado por comprar conosco!

Atenciosamente,
Sistema de Estoque
"""
    return send_email(to, subject, body)


def send_payment_failed_email(order_id: int, to: str, reason: str | None = None) -> bool:
    """Envia email avisando que o pagamento falhou."""
    subject = f"Pagamento do pedido #{order_id} falhou"
    body = f"""Olá!

Infelizmente houve um problema ao processar o pagamento do seu pedido #{order_id}.

Motivo: {reason or 'Não especificado'}

Por favor, verifique os dados do pagamento e tente novamente.

Se precisar de ajuda, responda este e-mail.

Atenciosamente,
Equipe de Pagamentos
"""
    return send_email(to, subject, body)
