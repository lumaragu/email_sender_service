import base64
from typing import Callable, Dict, List

import requests

from email_sender.email import Email, Attachment
from email_sender.email_service import EmailService
from email_sender.exceptions import EmailServiceError
from email_sender.exceptions import EmailServiceNonRetriableError

REQUEST_TIMEOUT = 180 # seconds


class PauboxEmailService(EmailService):

    def __init__(self, api_host: str, api_key: str, post_function: Callable = None):
        self._api_host = api_host
        self._api_key = api_key
        self._post = post_function or requests.post

    def send_email(self, email: Email):
        payload = self._format_payload(email)
        return self._send_payload_to_paubox(payload)

    def _format_payload(self, email: Email) -> Dict:
        return {
            "data": {
                "message": {
                    "headers": self._format_headers(email),
                    "recipients": email.recipients,
                    "content": self._format_content(email),
                    "attachments": self._format_attachments(email),
                    "allowNonTLS": False
                }
            }
        }

    def _format_headers(self, email: Email) -> Dict:
        return {
            "subject": email.subject,
            "from": email.sender,
            "reply-to": email.reply_to
        }

    def _format_content(self, email: Email) -> Dict:
        return {
            "text/html": self._encode_html_content(email.html_content) if email.html_content else "",
            "text/plain": email.text_content
        }

    def _encode_html_content(self, html_content: str) -> str:
        html_bytes = html_content.encode()
        return self._encode_b64_utf(html_bytes)

    @staticmethod
    def _encode_b64_utf(binary_content: bytes) -> str:
        return base64.b64encode(binary_content).decode()

    def _format_attachments(self, email: Email) -> List:
        return [self._format_attachment(attachment) for attachment in email.attachments]

    def _format_attachment(self, attachment: Attachment) -> Dict:
        return {
            "fileName": attachment.filename,
            "contentType": attachment.content_type,
            "content": self._encode_b64_utf(attachment.file_contents)
        }

    def _send_payload_to_paubox(self, payload: Dict):
        try:
            response = self._post(self._url, json=payload, headers=self._headers, timeout=REQUEST_TIMEOUT)
        except requests.exceptions.ConnectTimeout:
            print("Connection could not be established with Paubox. Will retry.")
            raise EmailServiceError
        except requests.exceptions.ReadTimeout:
            print("Read timeout. Paubox did not respond on time. Will not retry.")
            raise EmailServiceNonRetriableError

        if response.status_code != 200:
            raise EmailServiceError        
        return response

    @property
    def _url(self) -> str:
        return f"{self._api_host}/messages"

    @property
    def _headers(self) -> Dict[str, str]:
        return {"Authorization": self._auth_header}

    @property
    def _auth_header(self) -> str:
        return f"Token token={self._api_key}"
