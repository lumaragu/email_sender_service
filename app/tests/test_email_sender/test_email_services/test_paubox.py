import base64
import dataclasses
from unittest import TestCase, mock

import requests

from email_sender.email_services.paubox import PauboxEmailService, REQUEST_TIMEOUT
from email_sender.exceptions import EmailServiceError
from tests.test_email_sender.email_mixin import TestEmailMixin


class PauboxEmailServiceTests(TestCase, TestEmailMixin):

    def setUp(self) -> None:
        self.setUpEmail()

        self.api_host = "https://api.paubox.net/v1/test"
        self.api_key = "PAUBOX_API_KEY"

        self.init_mocks()

        self.service = PauboxEmailService(api_host=self.api_host, api_key=self.api_key, post_function=self.mock_post)

    def init_mocks(self):
        self.mock_post = mock.MagicMock(spec=requests.post)
        self.mock_response = mock.MagicMock(spec=requests.Response)
        self.mock_post.return_value = self.mock_response

    def test_send_email_success(self):
        self.mock_response.status_code = 200

        self.service.send_email(self.email)

        expected_payload = {
            "data": {
                "message": {
                    "headers": {
                        "subject": self.subject,
                        "from": self.sender,
                        "reply-to": self.reply_to
                    },
                    "recipients": self.recipients,
                    "content": {
                        "text/html": base64.b64encode(self.html_content.encode()).decode(),
                        "text/plain": self.text_content
                    },
                    "attachments": [
                        {
                            "fileName": self.attachment.filename,
                            "contentType": self.attachment.content_type,
                            "content": base64.b64encode(self.attachment.file_contents).decode()
                        }
                    ],
                    "allowNonTLS": False
                }
            }
        }

        self.mock_post.assert_called_once_with(
            url=f"{self.api_host}/messages",
            json=expected_payload,
            headers={"Authorization": f"Token token={self.api_key}"},
            timeout=REQUEST_TIMEOUT
        )

    def test_send_email_no_html_part(self):
        self.mock_response.status_code = 200

        self.email = dataclasses.replace(self.email, html_content=None)
        self.service.send_email(self.email)

        expected_payload = {
            "data": {
                "message": {
                    "headers": {
                        "subject": self.subject,
                        "from": self.sender,
                        "reply-to": self.reply_to
                    },
                    "recipients": self.recipients,
                    "content": {
                        "text/html": "",
                        "text/plain": self.text_content
                    },
                    "attachments": [
                        {
                            "fileName": self.attachment.filename,
                            "contentType": self.attachment.content_type,
                            "content": base64.b64encode(self.attachment.file_contents).decode()
                        }
                    ],
                    "allowNonTLS": False
                }
            }
        }

        self.mock_post.assert_called_once_with(
            url=f"{self.api_host}/messages",
            json=expected_payload,
            headers={"Authorization": f"Token token={self.api_key}"},
            timeout=REQUEST_TIMEOUT
        )

    def test_send_email_failed(self):
        self.mock_response.status_code = 500

        with self.assertRaises(EmailServiceError):
            self.service.send_email(self.email)
