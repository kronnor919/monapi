from email.message import EmailMessage

import aiosmtplib

from settings import SMTPSettings


class SMTPService:
    def __init__(self, config: SMTPSettings):
        self.host = config.host
        self.port = config.port
        self.sender_email = config.username
        self.sender_password = config.password

    async def send_email(self, email: str, subject: str, body: str):
        message = EmailMessage()
        message.set_content(body)
        message["Subject"] = subject
        message["From"] = self.sender_email
        message["To"] = email

        await aiosmtplib.send(
            message,
            hostname=self.host,
            port=self.port,
            start_tls=True,
            username=self.sender_email,
            password=self.sender_password,
        )
