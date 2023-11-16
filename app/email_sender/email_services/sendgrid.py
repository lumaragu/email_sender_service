import base64
from typing import List

import sendgrid
from python_http_client import HTTPError

from email_sender.email import Email, Attachment
from email_sender.email_service import EmailService
from email_sender.exceptions import EmailServiceError


class SendgridEmailService(EmailService):

    def __init__(self, sendgrid_client: sendgrid.SendGridAPIClient):
        self._sendgrid_client = sendgrid_client

    def send_email(self, email: Email):
        message = self._create_message(email)
        self._send_message(message)

    def _create_message(self, email: Email) -> sendgrid.Mail:
        message = self._init_message(email)
        message.reply_to = email.reply_to
        return self._add_attachments(message, email.attachments)

    def _init_message(self, email: Email) -> sendgrid.Mail:
        return sendgrid.Mail(
            from_email=email.sender,
            to_emails=email.recipients,
            subject=email.subject,
            plain_text_content=email.text_content,
            html_content=email.html_content
        )

    def _add_attachments(self, message: sendgrid.Mail, attachments: List[Attachment]) -> sendgrid.Mail:
        for attachment in attachments:
            sendgrid_attachment = self._make_sendgrid_attachment(attachment)
            message.add_attachment(sendgrid_attachment)

        return message

    def _make_sendgrid_attachment(self, attachment: Attachment) -> sendgrid.Attachment:
        return sendgrid.Attachment(
            file_name=attachment.filename,
            file_type=attachment.content_type,
            file_content=base64.b64encode(attachment.file_contents).decode()
        )

    def _send_message(self, message: sendgrid.Mail):
        try:
            self._sendgrid_client.send(message)
        except HTTPError:
            raise EmailServiceError
