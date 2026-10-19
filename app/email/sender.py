import smtplib
from email.message import EmailMessage

from app.core.config import settings
from app.utils.logger import logger


class EmailSender:

    @staticmethod
    def send(message: EmailMessage):
        try:
            with smtplib.SMTP_SSL(
                    settings.EMAIL_HOST,
                    settings.EMAIL_PORT
            ) as smtp:
                smtp.login(
                    settings.EMAIL_ADDRESS,
                    settings.EMAIL_PASSWORD
                )

                smtp.send_message(message)

        except Exception:
            logger.exception("Failed to send email")
            raise