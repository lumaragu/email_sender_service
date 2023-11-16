import base64
import dataclasses
import json
from unittest import TestCase

from email_sender.application import Application
from tests.test_email_sender.email_mixin import TestEmailMixin
from tests.test_email_sender.email_service import TestEmailService


class ApplicationTests(TestCase, TestEmailMixin):

    def setUp(self):
        self.setUpEmail()

        self.email_service = TestEmailService()

        self.application = Application(self.email_service)
        self.test_client = self.application.test_client()

    def test_email_sent_success(self):
        envelope = self.create_envelope()

        response = self.test_client.post("/", json=envelope)

        self.assertEqual(204, response.status_code)

        self.assertIn(self.email, self.email_service.sent_emails)

    def create_envelope(self):
        payload = {}

        if self.sender is not None:
            payload['email_from'] = self.sender

        if self.reply_to is not None:
            payload['reply_to'] = self.reply_to

        if self.recipients is not None:
            payload['recipients'] = self.recipients

        if self.subject is not None:
            payload['subject'] = self.subject

        if self.text_content is not None or self.html_content is not None:
            payload['content'] = {}

            if self.text_content is not None:
                payload['content']['text/plain'] = self.text_content

            if self.html_content is not None:
                payload['content']["text/html"] = self.html_content

        if self.attachment is not None:
            payload['optional_headers'] = {
                "attachments": [
                    {
                        "fileName": self.attachment.filename,
                        "contentType": self.attachment.content_type,
                        "content": base64.b64encode(self.attachment.file_contents).decode()
                    }
                ]
            }

        serialized_payload = json.dumps(payload)
        serialized_payload_b64 = base64.b64encode(serialized_payload.encode()).decode()
        return {"message": {"data": serialized_payload_b64}}

    def test_email_sent_failed(self):
        envelope = self.create_envelope()
        self.email_service.error = True

        response = self.test_client.post("/", json=envelope)

        self.assert_no_message_sent(response, status_code=202)

    def test_no_message(self):
        envelope = {}

        response = self.test_client.post("/", json=envelope)

        self.assert_no_message_sent(response)

    def assert_no_message_sent(self, response, status_code=202):
        self.assertEqual(status_code, response.status_code)
        self.assertEqual([], self.email_service.sent_emails)

    def test_no_data(self):
        envelope = {"message": {}}

        response = self.test_client.post("/", json=envelope)

        self.assert_no_message_sent(response)

    def test_undecodable_data(self):
        envelope = {"message": {"data": "ab d\9 =====h"}}

        response = self.test_client.post("/", json=envelope)

        self.assert_no_message_sent(response)

    def test_data_not_json(self):
        envelope = {"message": {"data": "ab dh"}}

        response = self.test_client.post("/", json=envelope)

        self.assert_no_message_sent(response)

    def test_no_recipients(self):
        self.recipients = None
        envelope = self.create_envelope()

        response = self.test_client.post("/", json=envelope)

        self.assert_no_message_sent(response)

    def test_no_email_from(self):
        self.sender = None
        envelope = self.create_envelope()

        response = self.test_client.post("/", json=envelope)

        self.assert_no_message_sent(response)

    def test_no_subject(self):
        self.subject = None
        envelope = self.create_envelope()

        response = self.test_client.post("/", json=envelope)

        self.assert_no_message_sent(response)

    def test_no_content(self):
        self.text_content = None
        self.html_content = None
        envelope = self.create_envelope()

        response = self.test_client.post("/", json=envelope)

        self.assert_no_message_sent(response)

    def test_no_optional_headers(self):
        self.attachment = None
        envelope = self.create_envelope()

        response = self.test_client.post("/", json=envelope)

        self.assertEqual(204, response.status_code)

        email = dataclasses.replace(self.email, attachments=[])
        self.assertIn(email, self.email_service.sent_emails)

    def test_no_text_content(self):
        self.text_content = None
        envelope = self.create_envelope()

        response = self.test_client.post("/", json=envelope)

        self.assert_no_message_sent(response, 202)

    def test_no_html_content(self):
        self.html_content = None
        envelope = self.create_envelope()

        response = self.test_client.post("/", json=envelope)

        self.email = dataclasses.replace(self.email, html_content=None)

        self.assertEqual(response.status_code, 204)
        self.assertIn(self.email, self.email_service.sent_emails)
