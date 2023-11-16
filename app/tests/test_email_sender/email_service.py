from email_sender.email import Email
from email_sender.email_service import EmailService
from email_sender.exceptions import EmailServiceError


class TestEmailService(EmailService):

    def __init__(self):
        self.error = False
        self.sent_emails = []

    def send_email(self, email: Email):
        if self.error:
            raise EmailServiceError

        self.sent_emails.append(email)
