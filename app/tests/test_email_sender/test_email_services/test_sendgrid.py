import base64
from unittest import TestCase, mock

import sendgrid
from python_http_client import HTTPError

from email_sender.email_services.sendgrid import SendgridEmailService
from email_sender.exceptions import EmailServiceError
from tests.test_email_sender.email_mixin import TestEmailMixin


class SendgridEmailServiceTests(TestCase, TestEmailMixin):

    class TestSendgridError(Exception):

        def __init__(self):
            self.code = 400
            self.reason = "Test"
            self.hdrs = {}

        def read(self):
            return "body"

    def setUp(self) -> None:
        self.setUpEmail()
        self.error = False
        self.sent_emails = []

        self.mock_sendgrid_client = mock.MagicMock(spec=sendgrid.SendGridAPIClient)
        self.mock_sendgrid_client.send.side_effect = self.send_email

        self.service = SendgridEmailService(self.mock_sendgrid_client)

    def test_send_email_success(self):
        self.service.send_email(self.email)

        expected_message = self.make_expected_message()

        self.assertIn(expected_message.get(), self.sent_emails)

    def send_email(self, message: sendgrid.Mail):
        if self.error:
            raise HTTPError(self.TestSendgridError())
        email = message.get()
        self.sent_emails.append(email)

    def make_expected_message(self) -> sendgrid.Mail:
        message = sendgrid.Mail(
            from_email=self.sender,
            to_emails=self.recipients,
            subject=self.subject,
            plain_text_content=self.text_content,
            html_content=self.html_content
        )
        message.reply_to = self.reply_to
        message.attachment = [
            sendgrid.Attachment(
                file_name=self.attachment.filename,
                file_type=self.attachment.content_type,
                file_content=base64.b64encode(self.attachment.file_contents).decode()
            )
        ]
        return message

    def test_send_email_failure(self):
        self.error = True

        self.service = SendgridEmailService(self.mock_sendgrid_client)

        with self.assertRaises(EmailServiceError):
            self.service.send_email(self.email)

        self.assertEqual([], self.sent_emails)
