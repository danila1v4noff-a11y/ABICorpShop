import os
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr
from typing import List

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("SMTP_USER"),
    MAIL_PASSWORD=os.getenv("SMTP_PASSWORD"),
    MAIL_FROM=os.getenv("SMTP_FROM"),
    MAIL_PORT=int(os.getenv("SMTP_PORT", 465)),
    MAIL_SERVER=os.getenv("SMTP_HOST"),
    MAIL_STARTTLS=True,      # ← меняем на True
    MAIL_SSL_TLS=False,      # ← меняем на False
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

async def send_email(recipients: List[EmailStr], subject: str, body: str):
    message = MessageSchema(
        subject=subject,
        recipients=recipients,
        body=body,
        subtype="html"
    )
    fm = FastMail(conf)
    await fm.send_message(message)