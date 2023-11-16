from typing import Dict

from google.cloud.secretmanager_v1 import SecretManagerServiceClient
from sendgrid import SendGridAPIClient

from email_sender.email_service import EmailService
from email_sender.email_services.paubox import PauboxEmailService
from email_sender.email_services.sendgrid import SendgridEmailService


class EmailServiceFactory:

    def __init__(self, environment: Dict[str, str], secretmanager_client: SecretManagerServiceClient):
        self._environment = environment
        self._secretmanager_client = secretmanager_client

    def create_service(self) -> EmailService:
        if "INSECURE_EMAILS" in self._environment:
            return self._create_sendgrid_email_service()
        else:
            return self._create_paubox_email_service()

    def _create_sendgrid_email_service(self) -> EmailService:
        api_key = self._read_secret("SENDGRID_API_KEY_SECRET")
        sendgrid_client = SendGridAPIClient(api_key)
        return SendgridEmailService(sendgrid_client)

    def _read_secret(self, secret_key: str) -> str:
        secret_name = self._environment[secret_key]
        secret_version_response = self._secretmanager_client.access_secret_version(secret_name)
        return secret_version_response.payload.data.decode()

    def _create_paubox_email_service(self) -> EmailService:
        api_host = self._environment['PAUBOX_API_HOST']
        api_key = self._read_secret("PAUBOX_API_KEY_SECRET")

        return PauboxEmailService(api_host, api_key)
