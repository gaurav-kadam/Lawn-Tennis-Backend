from datetime import datetime
from email.message import EmailMessage

from app.core.config import settings
from app.email.sender import EmailSender

from app.templates.email.plain_text import (
    registration_email_text,
    login_email_text,
    login_otp_email_text,
)

from app.templates.email.renderer import render_email_template


class EmailService:

    @staticmethod
    def send(
            to: str,
            subject: str,
            body: str,
            html: str,
    ):
        message = EmailMessage()

        message["Subject"] = subject
        message["From"] = (
            f"{settings.EMAIL_FROM_NAME} "
            f"<{settings.EMAIL_ADDRESS}>"
        )
        message["To"] = to

        message.set_content(body)

        if html:
            message.add_alternative(
                html,
                subtype="html",
            )

        EmailSender.send(message)

    @staticmethod
    def send_registration_email(
            to: str,
            user_name: str,
    ):
        body = registration_email_text(user_name)

        html = render_email_template(
            "registration.html",
            name=user_name,
            year=datetime.now().year,
        )

        EmailService.send(
            to=to,
            subject="Registration Successful",
            body=body,
            html=html,
        )

    @staticmethod
    def send_login_success_email(
            to: str,
            user_name: str,
    ):
        body = login_email_text(user_name)

        html = render_email_template(
            "login.html",
            name=user_name,
            year=datetime.now().year,
        )

        EmailService.send(
            to=to,
            subject="Login Successful",
            body=body,
            html=html,
        )

    @staticmethod
    def send_login_otp_email(
            to: str,
            user_name: str,
            otp: str,
    ):
        body = login_otp_email_text(
            user_name,
            otp,
        )

        html = render_email_template(
            "login_otp.html",
            name=user_name,
            otp=otp,
            year=datetime.now().year,
        )

        EmailService.send(
            to=to,
            subject="Login Verification Code",
            body=body,
            html=html,
        )