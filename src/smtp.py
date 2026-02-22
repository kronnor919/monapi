import os
from email.message import EmailMessage

import aiosmtplib


async def send_email(email: str, subject: str, body: str):
    smtp_email = os.getenv("SMTP_EMAIL")
    smtp_password = os.getenv("SMTP_PASSWORD")
    host = os.getenv("SMTP_HOST") or "smtp.gmail.com"

    if not smtp_email or not smtp_password:
        raise ValueError(
            "SMTP_EMAIL and SMTP_PASSWORD environment variables must be set"
        )

    message = EmailMessage()
    message.set_content(body)
    message["Subject"] = subject
    message["From"] = smtp_email
    message["To"] = email

    await aiosmtplib.send(
        message,
        hostname=host,
        port=587,
        start_tls=True,
        username=smtp_email,
        password=smtp_password,
    )
