import smtplib
from email.message import EmailMessage
from typing import Optional

from flask import current_app


class EmailDispatchError(RuntimeError):
    """Raised when an email could not be delivered."""


def _build_message(sender: str, recipient: str, subject: str, text_body: str, html_body: Optional[str] = None) -> EmailMessage:
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipient
    msg.set_content(text_body)

    if html_body:
        msg.add_alternative(html_body, subtype='html')

    return msg


def _open_smtp_connection():
    cfg = current_app.config
    host = cfg.get('MAIL_SERVER')
    if not host:
        raise EmailDispatchError('MAIL_SERVER is not configured')

    port = int(cfg.get('MAIL_PORT') or 587)
    username = cfg.get('MAIL_USERNAME')
    password = cfg.get('MAIL_PASSWORD')
    use_tls = cfg.get('MAIL_USE_TLS', True)
    use_ssl = cfg.get('MAIL_USE_SSL', False)
    timeout = int(cfg.get('MAIL_TIMEOUT', 10))

    try:
        if use_ssl:
            smtp = smtplib.SMTP_SSL(host=host, port=port, timeout=timeout)
        else:
            smtp = smtplib.SMTP(host=host, port=port, timeout=timeout)
            if use_tls:
                smtp.starttls()
        if username and password:
            smtp.login(username, password)
        return smtp
    except Exception as exc:  # pragma: no cover - network stack
        raise EmailDispatchError(f'failed to open SMTP connection: {exc}') from exc


def send_password_reset_email(recipient: str, code: str, expires_minutes: int) -> None:
    cfg = current_app.config
    sender = cfg.get('MAIL_SENDER') or cfg.get('MAIL_USERNAME')
    if not sender:
        raise EmailDispatchError('MAIL_SENDER or MAIL_USERNAME must be configured')
    if not recipient:
        raise EmailDispatchError('recipient email is missing')

    subject = cfg.get('MAIL_RESET_SUBJECT', '【药品监管平台】密码重置验证码')
    brand = cfg.get('MAIL_BRAND_NAME', '药品监管平台')
    text_body = (
        f'您正在使用 {brand} 的找回密码功能。\n'
        f'验证码：{code}\n'
        f'请在 {expires_minutes} 分钟内完成验证，切勿泄露给他人。'
    )
    html_body = (
        f'<p>您正在使用 <strong>{brand}</strong> 的找回密码功能。</p>'
        f'<p style="font-size:20px;font-weight:700;letter-spacing:2px;">验证码：{code}</p>'
        f'<p>验证码将在 <strong>{expires_minutes} 分钟</strong> 后失效，请勿泄露。</p>'
    )

    message = _build_message(sender, recipient, subject, text_body, html_body)
    smtp = _open_smtp_connection()
    try:
        smtp.send_message(message)
    except Exception as exc:  # pragma: no cover - network stack
        raise EmailDispatchError(f'failed to send email: {exc}') from exc
    finally:
        try:
            smtp.quit()
        except Exception:  # pragma: no cover - best effort cleanup
            pass
