import smtplib
import logging
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from dataclasses import dataclass

from twuaqirag.domain.reviews.models import Review
from twuaqirag.rag.rag_types import ReviewSentiment

logger = logging.getLogger(__name__)


@dataclass
class EmailConfig:
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    sender_email: str = ""
    sender_password: str = ""
    recipient_email: str = ""
    enabled: bool = False


class Email_Service:
    def __init__(self, config: Optional[EmailConfig] = None):
        self.config = config or EmailConfig()
        self._configure_from_env()

    def _configure_from_env(self):
        sender = os.getenv("EMAIL_SENDER")
        password = os.getenv("EMAIL_PASSWORD")
        recipient = os.getenv("EMAIL_RECIPIENT")

        logger.warning(
            f"ENV CHECK → sender={bool(sender)} password={bool(password)} recipient={bool(recipient)}"
        )

        if sender and password and recipient:
            self.config.sender_email = sender
            self.config.sender_password = password
            self.config.recipient_email = recipient
            self.config.enabled = True

            logger.info("📧 Email service enabled from env")

    def is_configured(self) -> bool:
        return self.config.enabled

    def send_alert(self, review: Review, place_name: Optional[str] = None):
        print("\n" + "=" * 50)
        print("🚨 NEGATIVE REVIEW ALERT 🚨")
        print(f"📍 Place: {place_name or review.place_id}")
        print(f"💬 Review: {review.text}")
        print("=" * 50)

        if not self.is_configured():
            print("📧 Email not configured — console only")
            return

        msg = MIMEMultipart()
        msg["From"] = self.config.sender_email
        msg["To"] = self.config.recipient_email
        msg["Subject"] = f"Negative Review - {place_name or review.place_id}"

        msg.attach(MIMEText(review.text, "plain"))

        with smtplib.SMTP(self.config.smtp_server, self.config.smtp_port) as server:
            server.starttls()
            server.login(
                self.config.sender_email, self.config.sender_password
            )
            server.send_message(msg)

        logger.info("📧 Email sent successfully")
