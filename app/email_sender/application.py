import base64
import binascii
import hashlib
import json

from flask import Flask, request

from email_sender.email import Email, Attachment
from email_sender.email_service import EmailService
from email_sender.exceptions import EmailServiceError
from email_sender.exceptions import EmailServiceNonRetriableError
from email_sender.utils import BqConnector


class Application(Flask):

    def __init__(self, email_service: EmailService):
        super(Application, self).__init__("email-sender")
        self._email_service = email_service
        self._add_routes()

    def _add_routes(self):
        self.add_url_rule("/", "index", self._index, methods=['POST'])

    def _index(self):
        envelope = request.get_json()
        try:
            pubsub_message = envelope['message']
        except KeyError:
            return "", 202

        try:
            message_data_b64 = pubsub_message['data']
        except KeyError:
            return "", 202

        try:
            message_data = base64.b64decode(message_data_b64).decode()
        except (UnicodeDecodeError, binascii.Error):
            return "", 202

        try:
            data = json.loads(message_data)
        except ValueError:
            return "", 202

        try:
            email_from = data['email_from']
            recipients = data['recipients']
            subject = data['subject']
            content = data['content']
        except KeyError:
            return "", 202

        reply_to = data.get("reply_to", email_from)

        optional_headers = data.get('optional_headers', {})
        attachments = optional_headers.get('attachments', [])

        text_content = content.get("text/plain")
        if not text_content:
            print("No text content found in the message.")
            return "", 202

        html_content = content.get("text/html")
        if not html_content:
            print("No html content found in the message.")

        email = Email(
            sender=email_from,
            reply_to=reply_to,
            recipients=recipients,
            subject=subject,
            text_content=text_content,
            html_content=html_content,
            attachments=[
                Attachment(
                    filename=attachment['fileName'],
                    content_type=attachment['contentType'],
                    file_contents=base64.b64decode(attachment['content'])
                )
                for attachment in attachments if attachments
            ]
        )

        content_hash = hashlib.sha256(text_content.encode()).hexdigest()

        try:
            email_response = self._email_service.send_email(email)
            if data.get("client_id") and data.get("bio_id") and email_response:
                BqConnector().write(data, email_response)
        except EmailServiceError:
            print("Unable to send the email.")
            print("Failed delivery content: '{}'.".format(content_hash))
            return "", 202
        except EmailServiceNonRetriableError:
            return "", 202

        print("Successfully delivered content: '{}'.".format(content_hash))

        return "", 204
