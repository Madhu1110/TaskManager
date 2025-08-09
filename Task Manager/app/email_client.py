# app/email_client.py
import os
from typing import Dict

EMAIL_PROVIDER = os.getenv("EMAIL_PROVIDER", "smtp")  # "smtp" or "sendgrid"

class BaseEmailClient:
    def send(self, to_email: str, subject: str, body: str):
        raise NotImplementedError

class SMTPEmailClient(BaseEmailClient):
    def __init__(self):
        import smtplib
        from email.mime.text import MIMEText
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.example.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))
        self.username = os.getenv("SMTP_USER", "")
        self.password = os.getenv("SMTP_PASS", "")

    def send(self, to_email: str, subject: str, body: str):
        import smtplib
        from email.mime.text import MIMEText
        msg = MIMEText(body, "html")
        msg["Subject"] = subject
        msg["From"] = os.getenv("EMAIL_FROM", "no-reply@example.com")
        msg["To"] = to_email

        server = smtplib.SMTP(self.smtp_host, self.smtp_port)
        server.starttls()
        if self.username:
            server.login(self.username, self.password)
        server.sendmail(msg["From"], [to_email], msg.as_string())
        server.quit()

class SendGridClient(BaseEmailClient):
    def __init__(self):
        import os
        self.api_key = os.getenv("SENDGRID_API_KEY")

    def send(self, to_email: str, subject: str, body: str):
        # minimal implementation using requests; in docker env you'll need network access
        import requests
        payload = {
            "personalizations": [{"to": [{"email": to_email}]}],
            "from": {"email": os.getenv("EMAIL_FROM", "no-reply@example.com")},
            "subject": subject,
            "content": [{"type": "text/html", "value": body}],
        }
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        r = requests.post("https://api.sendgrid.com/v3/mail/send", json=payload, headers=headers)
        r.raise_for_status()

def get_email_client():
    if EMAIL_PROVIDER == "sendgrid":
        return SendGridClient()
    return SMTPEmailClient()
