from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from jinja2 import Environment, select_autoescape, FileSystemLoader
from pathlib import Path
from pydantic import EmailStr
from typing import Dict, Any
from loguru import logger

from andromeda_ng.service.settings import config

# Email configuration
email_conf = ConnectionConfig(
    MAIL_USERNAME=config.MAIL_USERNAME,
    MAIL_PASSWORD=config.MAIL_PASSWORD,
    MAIL_FROM=config.MAIL_FROM,
    MAIL_PORT=config.MAIL_PORT,
    MAIL_SERVER=config.MAIL_SERVER,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True
)

templates_path = Path(__file__).parent.parent / "templates"
env = Environment(
    loader=FileSystemLoader(templates_path),
    autoescape=select_autoescape(['html', 'xml'])
)


async def send_password_reset_email(
    email_to: EmailStr,
    username: str,
    reset_token: str
) -> None:
    """
    Send password reset email with token

    Args:
        email_to: Recipient email address
        username: Username of the recipient
        reset_token: Password reset token
    """
    try:
        # Get template
        template = env.get_template("password_reset.html")

        # Build reset URL
        reset_url = f"{config.FRONTEND_URL}/reset-password?token={reset_token}"

        # Render template with context
        html = template.render(
            username=username,
            reset_url=reset_url,
            valid_hours=24  # Token validity period
        )

        # Create message
        message = MessageSchema(
            subject="Password Reset Request",
            recipients=[email_to],
            body=html,
            subtype="html"
        )

        # Send email
        fm = FastMail(email_conf)
        await fm.send_message(message)
        logger.info(f"Password reset email sent to {email_to}")

    except Exception as e:
        logger.error(f"Failed to send password reset email: {e}")
        raise
